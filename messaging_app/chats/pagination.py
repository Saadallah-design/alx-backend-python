"""
Pagination classes for the chats app.

This module defines custom pagination classes to control
how data is paginated in API responses.
"""

from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    """
    Pagination class specifically for Message instances.
    
    Returns 20 messages per page with pagination metadata including:
    - count: Total number of messages
    - next: URL to the next page (if available)
    - previous: URL to the previous page (if available)
    - results: Array of message objects for the current page
    
    Usage:
        Apply this to MessageViewSet to automatically paginate message listings.
        
    Example API Response:
        {
            "count": 45,
            "next": "http://api.example.com/messages/?page=4",
            "previous": null,
            "results": [
                { message objects... }
            ]
        }
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
