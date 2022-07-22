import scrapy
from bs4 import BeautifulSoup, element


class ElixierSpider(scrapy.Spider):
    name = 'elixier-spider'

    start_urls = ["https://www.bildungsserver.de/elixier/elixier2_list.php?" \
        "feldname2=Systematik%2FFach&" \
        "feldinhalt2=%22mathematisch-naturwissenschaftliche+F%C3%A4cher%22&" \
        "bool2=and&" \
        "feldname3=Systematik%2FFach&" \
        "feldinhalt3=%22Chemie%22&" \
        "bool3=and&" \
        "&" \
        "suche=erweitert&" \
        "t=Suchen"]

    def parse(self, response, position=0):
        metadata_links = []
        for result in response.css('ul.search-list li'):
            metadata_links.append(
                response.follow(
                    result.css('h2 a')[0],
                    self.parse_detail_page,
                    cb_kwargs={'position': position}))
            position += 1

        next_page_el = response.xpath('//a/img[@alt="Eine Seite vor"]/parent::a')
        if next_page_el:
            next_page_reqs = [response.follow(next_page_el[0], self.parse, cb_kwargs={'position': position})]
        else:
            next_page_reqs = []
        return metadata_links + next_page_reqs

    def parse_detail_page(self, response, position):
        self.logger.info('parsing %s', response.url)
        soup = BeautifulSoup(response.text, features='lxml')
        search_content = soup.find('div', {'class': 'search-content'})
        out = dict()
        out['position'] = position
        tags = [child for child in search_content.children if type(child) == element.Tag]
        if tags[0].name == 'h1':
            out['title'] = tags[0].text
        else:
            raise Exception("Coudln't find title")

        if tags[1].name == 'p':
            out['description'] = tags[1].text
        else:
            raise Exception("Couldn't find description")

        if (tags[1].name == 'p') and (tags[1].find('a').get('href')):
            out['url'] = tags[1].find('a')['href']
        else:
            raise Exception("Couldn't find url")

        if tags[3].name == 'p':
            out['description'] = tags[3].text
        else:
            raise Exception("Couldn't find description")

        key = None
        for tag in tags[4:]:
            if tag.name == 'h4':
                key = tag.text
            if tag.name == 'p':
                value = tag.text
                out[key] = value
        return out
