 # -*- coding: utf-8 -*-
import scrapy
import urlparse

class News(scrapy.Item):
  article_id = scrapy.Field()
  headline = scrapy.Field()
  subhead = scrapy.Field()
  author = scrapy.Field()
  published_at = scrapy.Field()
  modified_at = scrapy.Field()
  tags = scrapy.Field()
  content = scrapy.Field()
  images = scrapy.Field()
  link = scrapy.Field()
  section = scrapy.Field()

class NewsSpider(scrapy.Spider):
  name = 'news-spider'

  def __init__(self):
    self.start_urls = ['http://www.atribuna.com.br/']

  def parse(self, response):
    menu = response.css(".dropdown-toggle")
    
    for i in menu:
      link = i.xpath("@href")[0].extract().strip()
      section = i.xpath("text()")[0].extract().strip()
      if(link.find("atribuna")):
        page_url = urlparse.urljoin(response.url, link)
        yield scrapy.Request(page_url, callback=self.pagination, meta={'section':section})


  def pagination(self,response):    
    page = response.css(".listagem-paginacao-pages > li > a")
    section = response.meta['section']

    for p in page:      
      if int(p.xpath('text()')[0].extract()) > 2:
        break

      link = p.xpath('@href')[0].extract()      
      page_url = urlparse.urljoin("http://www.atribuna.com.br/", link)
      yield scrapy.Request(page_url, callback=self.section_content, meta={'section':section})


  def section_content(self,response):    
    news = response.css(".listagem-item > a")
    section = response.meta['section']

    for n in news:
      link = n.xpath('@href')[0].extract()      
      page_url = urlparse.urljoin("http://www.atribuna.com.br/", link)
      yield scrapy.Request(page_url, callback=self.news_content, meta={'section':section})

  def news_content(self,response):    
    section = response.meta['section']
    headline = response.css(".single-header-title::text").extract_first()
    subhead = response.css(".single-header-subheader::text").extract_first()
    author = response.css(".single-header-author-name::text").extract_first()
    published_at = response.xpath("//meta[@itemprop='datePublished']/@content")[0].extract()
    modified_at = response.xpath("//meta[@itemprop='dateModified']/@content")[0].extract()
    try:
      images = response.xpath("//table[@class='contenttable' or @class='image-middle']")    
    except:
      pass
    hash = response.url.find("cHash")
    id = response.url[hash+6:]
    content = ""
    tags = []
    img = []
    
    content_div = response.css(".bodytext")
    tags_div = response.css(".single-keywords ul li a")

    for i in images:
        single_image = urlparse.urljoin("http://www.atribuna.com.br/", i.xpath("//img/@src")[0].extract())
        single_image_title = i.css("tbody > tr > td::text").extract_first()

        img.append({'src': single_image, 'title': single_image_title})


    for i in content_div:
      if len(i.xpath("text()")) > 0 :
        content+= i.xpath("text()")[0].extract().strip()

    for t in tags_div:  
      if len(t.xpath("text()")) > 0 :    
        tags.append(t.xpath("text()")[0].extract().strip())
     

    news = News()
    news["article_id"] = id
    news["section"] = section
    news["headline"] = headline
    news["subhead"] = subhead
    news["author"] = author
    news["published_at"] = published_at
    news["modified_at"] = modified_at
    news["link"] = response.url 
    news["content"] = content
    news["tags"] = tags
    news["images"] = img

    yield {
      'article_id': id,
      'section' : section,
      'headline' : headline,
      'subhead' : subhead,
      'author' : author,
      'published_at' : published_at,
      'modified_at' : modified_at,
      'link' : response.url,
      'content' : content,
      'images' : img,
      'tags' : tags      
    }