# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.http import Request

import os
import re

class AutoMlSpider(scrapy.Spider):
    name = 'auto_ml'
    
    def start_requests(self):

        initial_url = 'https://autos.mercadolibre.com.uy/1980'
        yield Request(url = initial_url, callback = self.parse_years)

    def parse_years(self,response):
    	'obtenemos las grillas para cada año'
    	'las grillas solamente van hasta la pagina 42'

    	print('entramos en parse_years?')
    	print('esta es la response: ', response)

    	listings = response.xpath('//*[@class="ui-search-result__content ui-search-link"]/@href').extract()

    	for listing in listings:
    		yield Request(url=listing, callback = self.parse_cars)
        try:
            next_page = response.xpath('//*[@class="andes-pagination__link ui-search-link"]')[-1].extract()
            if (next_page) and ('Siguiente' in next_page):
                print('nueva version', next_page)
                result = re.search('href="(.*)" class', next_page)
                absolute_link = result.group(1)
                yield Request(absolute_link, callback = self.parse_years)
            elif next_page:
                if int(str(response).split('/')[-1][:4])+1 < 2022:
                    new_year = str(int(str(response).split('/')[-1][:4])+1)
                    uy = 'uy/'
                    ml = str(response)[5:].split('uy')[0]
                    full_url = ml + uy + new_year
                    print('next year is gonna be: ', full_url)
                    yield Request(full_url, callback = self.parse_years)
                else:
                    pass
        except:
            if int(str(response).split('/')[-1][:4])+1 < 2022:
                new_year = str(int(str(response).split('/')[-1][:4])+1)
                uy = 'uy/'
                ml = str(response)[5:].split('uy')[0]
                full_url = ml + uy + new_year
                print('next year is gonna be: ', full_url)
                yield Request(full_url, callback = self.parse_years)
            else:
                pass

    def parse_cars(self,response):
    	'extraemos informacion de los vehiculos'
    	print('entramos en parse_cars')
    	print(response)

    	tmp = {}

    	link_vehiculo = str(response)[5:-1]
    	fecha_pub_raw = response.xpath('//*[@id="short-desc"]/div/article[2]/dl/dd/text()').extract_first()
    	description = response.xpath('//*[@id="short-desc"]/div/header/h1/text()').extract_first()
    	precio_symbol = response.xpath('//*[@id="short-desc"]/div/fieldset/span/span[1]/text()').extract_first()
    	precio = response.xpath('//*[@id="short-desc"]/div/fieldset/span/span[2]/text()').extract_first()

    	#poblamos diccionario
    	tmp['link_vehiculo'] = link_vehiculo
    	tmp['fecha_publicacion'] = fecha_pub_raw
    	tmp['descripcion'] = description
    	tmp['precio_symbol'] = precio_symbol
    	tmp['precio'] = precio

    	#grilla de specs
    	keys_grilla = response.xpath('//*[@class="specs-list"]//*[@class="specs-item"]/strong/text()').extract()
    	values_grilla = response.xpath('//*[@class="specs-list"]//*[@class="specs-item"]/span/text()').extract()
    	#actualizamos dic con grilla de specs
    	tmp.update(dict(zip(keys_grilla, values_grilla)))

    	yield tmp