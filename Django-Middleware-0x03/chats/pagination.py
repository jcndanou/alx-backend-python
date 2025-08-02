from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    page_size = 20  # Nombre d'éléments par page
    page_size_query_param = 'page_size'  # Permet de changer la taille via ?page_size=X
    max_page_size = 100  # Taille maximale autorisée

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # Total des éléments
            'next': self.get_next_link(),  # URL de la page suivante
            'previous': self.get_previous_link(),  # URL de la page précédente
            'results': data,  # Les données paginées
            'page_size': self.page_size,  # Taille de la page actuelle
            'total_pages': self.page.paginator.num_pages  # Nombre total de pages
        })