from rest_framework.pagination import PageNumberPagination

class ShopPagination(PageNumberPagination):
    page_size = 4 
    page_size_query_param = 'size' # {baseurl}/size=10 

    max_page_size = 50 
    page_query_param = 'page' 
class ProductPagination(PageNumberPagination):
    page_size=4
    page_size_query_param='size'

    max_page_size=50
    page_query_param='page'

class CategoryPagination(PageNumberPagination):
    page_size=4
    page_query_param='size'

    max_page_size=50
    page_query_param='page'