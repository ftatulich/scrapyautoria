from abc import ABC

import scrapy


class FullAutoriaSpider(scrapy.Spider, ABC):
    name = 'autoria'
    allowed_domains = ['auto.ria.com']
    autoria_link = "https://auto.ria.com"

    # pass on new and used cars
    def start_requests(self):
        links = [
            "https://auto.ria.com/uk/car/used/",
            "https://auto.ria.com/uk/newauto/catalog/"
        ]
        for link in links:
            # check which type of car is referenced, for each type call the appropriate function
            if link == "https://auto.ria.com/uk/car/used/":
                yield scrapy.Request(link, callback=self.used_car_links)
            else:
                yield scrapy.Request(link, callback=self.new_brands)

    def used_car_links(self, response):
        pass

    # collect links to each brand of car
    def new_brands(self, response):
        print("new_brand")
        brand_links = response.xpath('.//div[@id="listAllMarks"]//a/@href').getall()
        original_links = set(brand_links)

        # in addition to links to car models,
        # the page contains links to the history of car brands, get rid of them
        new_links = []
        for link in original_links:
            if link.find("timeline") == -1:
                new_links.append(link)

        for link in new_links:
            yield scrapy.Request(self.autoria_link + link, callback=self.brand_models)
            break

    # search of models of each brand
    def brand_models(self, response):
        links = response.xpath('.//*[@id="models_range"]//a/@href').getall()
        if not links:
            links = response.xpath('//section[@class="gallery-view-brand box-panel"]/a/@href').getall()
            for link in links:
                print(self.autoria_link + link)
                yield scrapy.Request(self.autoria_link + link, callback=self.parse_new_car_another)
                break
        else:
            for link in links:
                print(self.autoria_link + link)
                yield scrapy.Request(self.autoria_link + link, callback=self.new_cars)
                break

    # collect and follow the links to each car
    def new_cars(self, response):
        cars_count = int(response.xpath('//span[@class="size16 bold resultsCount"]/text()').get())

        cars_links = response.xpath('//section[@class="proposition"]/a/@href').getall()

        for link in cars_links[:cars_count]:
            print(link)
            yield scrapy.Request(self.autoria_link + link, callback=self.parse_new_car)
            break

    @staticmethod
    # we collect data about the car
    def parse_new_car(response):
        name = response.xpath('//h3[@class="auto-content_title"]/text()').get()
        year = response.xpath('//h3[@class="auto-content_title"]/a/text()').get()
        city = response.xpath('//ul[@class="checked-list unstyle"]/li[2]/div[@class="item_inner"]/text()[1]').getall()
        price = response.xpath('//span[@class="price_value"]/text()').get()

        description = response.xpath('//div[@class="mb-10"]/text()').getall()
        description = " ".join(description)

        phone = response.xpath('//div[@class="fixed-phones-m_bg"]//a/@href').getall()
        image = response.xpath('//section[@id="infocar-video"]//img/@src').get()

        yield {
            "type": "new",
            "name": name,
            "year": year,
            "url": response.url,
            "price": price,
            "image": image,
            "city": city[1],
            "description": description,
            "phone": phone
        }

    @staticmethod
    # we collect data about the car
    def parse_new_car_another(response):
        print(response.url)


