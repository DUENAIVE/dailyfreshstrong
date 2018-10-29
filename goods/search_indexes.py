from haystack import indexes
from goods.models import GoodsSKU

#指定对某个类创建索引
# 索引名格式:模型名称+Index
class GoodsSKUIndex(indexes.SearchIndex,indexes.Indexable):
    # 索引字段use_template=True指定根据哪些字段建立索引文件的说明放在一个文件
    text=indexes.CharField(use_template=True, document=True)

    def get_model(self):
        # 返回你的模型类
        return GoodsSKU
    # 建立索引的数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()