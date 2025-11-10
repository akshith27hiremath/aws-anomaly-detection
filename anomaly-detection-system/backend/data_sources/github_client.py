"""
GitHub data source client using GitHub REST API.
Fetches repository metrics like commits, issues, PRs, and stars.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from backend.utils.config import get_detection_config, get_settings
from backend.utils.helpers import RateLimiter

logger = logging.getLogger(__name__)


class GitHubClient:
    """
    Client for fetching GitHub repository data.
    """

    def __init__(self):
        """Initialize the GitHub client."""
        self.settings = get_settings()
        self.config = get_detection_config()
        self.base_url = self.settings.github_base_url
        self.token = self.settings.github_token

        # Get GitHub configuration
        github_config = self.config.get_data_source_config('github')
        self.repositories = github_config.get('repositories', [])
        self.metrics = github_config.get('metrics', ['commit_count', 'issue_count', 'pr_count'])

        # Rate limiter: 60 calls per hour for authenticated, 5000 for token
        max_calls = 5000 if self.token else 60
        self.rate_limiter = RateLimiter(max_calls=max_calls, time_window=3600)

        # Cache for recent data
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl = 120  # seconds

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch GitHub data for configured repositories.

        Returns:
            List of data points with timestamp and values
        """
        if not self._should_fetch():
            logger.debug("Using cached GitHub data")
            return self._format_cached_data()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Fetch data for all repositories
                tasks = [self._fetch_repo_data(client, repo) for repo in self.repositories]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                data_points = []
                timestamp = datetime.now()

                for repo, result in zip(self.repositories, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error fetching {repo}: {result}")
                        continue

                    if result:
                        # Store in cache
                        self.cache[repo] = result

                        # Create data points for each metric
                        for metric in self.metrics:
                            value = result.get(metric)
                            if value is not None:
                                data_points.append({
                                    'source': 'github',
                                    'repository': repo,
                                    'metric': metric,
                                    'value': value,
                                    'timestamp': timestamp,
                                    'metadata': {
                                        'api': 'github',
                                        'raw_data': result
                                    }
                                })

                self.cache_timestamp = timestamp
                logger.info(f"Fetched {len(data_points)} GitHub data points")
                return data_points

        except Exception as e:
            logger.error(f"Error in GitHub data fetch: {e}")
            return []

    async def _fetch_repo_data(
        self,
        client: httpx.AsyncClient,
        repo: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data for a single repository.

        Args:
            client: HTTP client
            repo: Repository name (format: "owner/repo")

        Returns:
            Dictionary with repository data or None
        """
        # Check rate limit
        if not self.rate_limiter.can_proceed():
            logger.warning("Rate limit reached for GitHub API")
            await asyncio.sleep(60)

        try:
            # Fetch repository info
            repo_info = await self._fetch_repo_info(client, repo)
            if not repo_info:
                return None

            # Fetch recent commits
            commit_count = await self._fetch_recent_commits(client, repo)

            # Fetch recent issues
            issue_count = await self._fetch_recent_issues(client, repo)

            # Fetch recent PRs
            pr_count = await self._fetch_recent_prs(client, repo)

            return {
                'stars': repo_info.get('stargazers_count', 0),
                'forks': repo_info.get('forks_count', 0),
                'watchers': repo_info.get('watchers_count', 0),
                'open_issues': repo_info.get('open_issues_count', 0),
                'commit_count': commit_count,
                'issue_count': issue_count,
                'pr_count': pr_count,
                'size': repo_info.get('size', 0),  # KB
                'updated_at': repo_info.get('updated_at'),
            }

        except Exception as e:
            logger.error(f"Error fetching {repo}: {e}")
            return None

    async def _fetch_repo_info(
        self,
        client: httpx.AsyncClient,
        repo: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch basic repository information."""
        url = f"{self.base_url}/repos/{repo}"
        headers = self._get_headers()

        response = await client.get(url, headers=headers)
        self.rate_limiter.record_call()

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.error(f"Repository not found: {repo}")
        elif response.status_code == 403:
            logger.warning("GitHub API rate limit exceeded")
        else:
            logger.error(f"GitHub API error for {repo}: {response.status_code}")

        return None

    async def _fetch_recent_commits(
        self,
        client: httpx.AsyncClient,
        repo: str,
        hours: int = 24
    ) -> int:
        """
        Fetch count of recent commits.

        Args:
            client: HTTP client
            repo: Repository name
            hours: Look back this many hours

        Returns:
            Number of commits
        """
        url = f"{self.base_url}/repos/{repo}/commits"
        headers = self._get_headers()

        # Calculate since timestamp
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        params = {
            'since': since.isoformat(),
            'per_page': 100
        }

        try:
            response = await client.get(url, headers=headers, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                commits = response.json()
                return len(commits)
        except Exception as e:
            logger.error(f"Error fetching commits for {repo}: {e}")

        return 0

    async def _fetch_recent_issues(
        self,
        client: httpx.AsyncClient,
        repo: str,
        hours: int = 24
    ) -> int:
        """
        Fetch count of recently created issues.

        Args:
            client: HTTP client
            repo: Repository name
            hours: Look back this many hours

        Returns:
            Number of issues
        """
        url = f"{self.base_url}/repos/{repo}/issues"
        headers = self._get_headers()

        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        params = {
            'since': since.isoformat(),
            'state': 'all',
            'per_page': 100
        }

        try:
            response = await client.get(url, headers=headers, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                issues = response.json()
                # Filter out pull requests (they appear in issues endpoint)
                actual_issues = [i for i in issues if 'pull_request' not in i]
                return len(actual_issues)
        except Exception as e:
            logger.error(f"Error fetching issues for {repo}: {e}")

        return 0

    async def _fetch_recent_prs(
        self,
        client: httpx.AsyncClient,
        repo: str,
        hours: int = 24
    ) -> int:
        """
        Fetch count of recently created pull requests.

        Args:
            client: HTTP client
            repo: Repository name
            hours: Look back this many hours

        Returns:
            Number of PRs
        """
        url = f"{self.base_url}/repos/{repo}/pulls"
        headers = self._get_headers()

        params = {
            'state': 'all',
            'sort': 'created',
            'direction': 'desc',
            'per_page': 100
        }

        try:
            response = await client.get(url, headers=headers, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                prs = response.json()
                # Count PRs created in the last N hours
                since = datetime.now(timezone.utc) - timedelta(hours=hours)
                recent_prs = [
                    pr for pr in prs
                    if datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00')) > since
                ]
                return len(recent_prs)
        except Exception as e:
            logger.error(f"Error fetching PRs for {repo}: {e}")

        return 0

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AnomalyDetectionSystem/1.0'
        }

        if self.token:
            headers['Authorization'] = f'token {self.token}'

        return headers

    def _should_fetch(self) -> bool:
        """Check if new data should be fetched or use cache."""
        if not self.cache_timestamp:
            return True

        elapsed = (datetime.now() - self.cache_timestamp).total_seconds()
        return elapsed >= self.cache_ttl

    def _format_cached_data(self) -> List[Dict[str, Any]]:
        """Format cached data as data points."""
        data_points = []
        timestamp = self.cache_timestamp or datetime.now()

        for repo, data in self.cache.items():
            for metric in self.metrics:
                value = data.get(metric)
                if value is not None:
                    data_points.append({
                        'source': 'github',
                        'repository': repo,
                        'metric': metric,
                        'value': value,
                        'timestamp': timestamp,
                        'metadata': {
                            'cached': True,
                            'api': 'github'
                        }
                    })

        return data_points

    async def get_historical_activity(
        self,
        repo: str,
        weeks: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical activity statistics.

        Args:
            repo: Repository name
            weeks: Number of weeks of history

        Returns:
            List of weekly activity data points
        """
        url = f"{self.base_url}/repos/{repo}/stats/commit_activity"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    # Take last N weeks
                    recent_data = data[-weeks:] if len(data) > weeks else data

                    data_points = []
                    for week_data in recent_data:
                        timestamp = datetime.fromtimestamp(week_data['week'])
                        data_points.append({
                            'source': 'github',
                            'repository': repo,
                            'metric': 'commit_count',
                            'value': week_data['total'],
                            'timestamp': timestamp
                        })

                    return data_points
                else:
                    logger.error(f"Error fetching activity: {response.status_code}")

        except Exception as e:
            logger.error(f"Error in historical activity fetch: {e}")

        return []
