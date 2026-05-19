"""
SharePoint data source — placeholder for future MS SharePoint API integration.

When implemented this will connect to the Microsoft Graph API (or SharePoint
REST API) to fetch MS List items directly, replacing the manual CSV export step.

Credentials will be obtained via OAuth2 / service-principal authentication.
The raw records returned will be shaped to match the same dict structure that
CSVDataSource produces so that the transformer layer needs no changes.
"""

from typing import Any

from .base import DataSource


class SharePointDataSource(DataSource):
    """
    Future MS SharePoint / Graph API data source.

    Constructor parameters (for reference — not yet functional):

        site_url    Full SharePoint site URL, e.g.
                    'https://iciq.sharepoint.com/sites/Automatitzacions'
        list_name   Display name of the MS List, e.g.
                    'Template Automatització'
        tenant_id   Azure AD tenant ID for OAuth2
        client_id   App registration client ID
        client_secret  App registration client secret (or use cert auth)
    """

    def __init__(
        self,
        site_url: str,
        list_name: str,
        tenant_id: str = "",
        client_id: str = "",
        client_secret: str = "",
    ):
        raise NotImplementedError(
            "SharePointDataSource is not yet implemented.\n"
            "Please use CSVDataSource with a manually exported CSV file.\n\n"
            "Implementation roadmap:\n"
            "  1. Authenticate via msal (Microsoft Authentication Library)\n"
            "  2. Call Graph API: GET /sites/{site}/lists/{list}/items\n"
            "  3. Map Graph API field names to CSV column names\n"
            "  4. Return records in the same dict shape as CSVDataSource"
        )

    def fetch_all(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def fetch_by_id(self, internal_id: str) -> dict[str, Any]:
        raise NotImplementedError

    def fetch_by_index(self, index: int) -> dict[str, Any]:
        raise NotImplementedError
