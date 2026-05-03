from import_export import resources
from .models import Stock, JCBPart

class StockResource(resources.ModelResource):
    class Meta:
        model = Stock

class JCBPartResource(resources.ModelResource):
    class Meta:
        model = JCBPart
        import_id_fields = ('part_number',)
        fields = ('part_number', 'name', 'description', 'price', 'stock_quantity', 'category')
