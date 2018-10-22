from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FDFSStorage(Storage):
    def __init__(self):
        self.fdfs_conf = settings.FDFS_CLIENT_CONF
        self.fdfs_url = settings.FDFS_URL

    def _open(self, name, mode='rb'):
        '''打开文件'''
        pass

    def _save(self, name, content):
        '''保存文件'''
        # 创建Fdfs_client对象
        client = Fdfs_client(self.fdfs_conf)
        # 上传文件到FastDFS系统中
        ret = client.upload_by_buffer(content.read())
        print('ret',ret)
        # 查看上传状态
        if ret.get('Status') != 'Upload successed.':
            # 抛出异常
            raise Exception('上传失败')
        # 获取返回的文件id名
        filename=ret.get("Remote file_id").decode()
        # 将文件id名返回
        return filename

    def exists(self, name):
        '''django判断文件名是否可用'''
        # 返回false则保存,返回True则不保存
        return False

    def url(self, name):
        '''返回访问文件的路径'''
        return self.fdfs_url + name
