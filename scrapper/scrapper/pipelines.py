# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

class ScrapperPipeline:
    def process_item(self, item, spider):
        return item


from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request

class CustomImageNamePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item.get('image_urls', []):
            image_name = item.get('title')  # Use title as the image name
            if image_name:  # Ensure there's a title
                yield Request(image_url, meta={'image_name': image_name})


    def file_path(self, request, response=None, info=None, *, item=None):
        image_name = request.meta.get('image_name', 'default_name')
        image_ext = request.url.split('.')[-1]
        filename = f'{image_name}.{image_ext}'
        return filename
