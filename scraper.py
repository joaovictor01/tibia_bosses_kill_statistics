class Scraper:
    """ Class responsible for general scraping operations"""
    soup = None

    def __init__(self, url=None, soup=None):
        if url:
            self.url = url
            self.scrap_root_url()
        if soup:
            self.set_soup(soup)

    def scrap_root_url(self):
        """ Start the BeautifulSoup object of the given url """
        req = requests.get(self.url, verify=False)
        self.soup = BeautifulSoup(req.content, 'html.parser')

    def get_all_hrefs(self):
        """ Return all href elements """
        return self.soup.findAll('a', href=True)

    @staticmethod
    def scrap_url(url):
        """ Return the BeautifulSoup object of a given url """
        children_req = requests.get(url, verify=False)
        return BeautifulSoup(children_req.content, 'html.parser')
    
    def find_all_occurrences_of_str(self, string):
        """ Return a list of string with all occurrences of a string """
        return self.soup.find_all(string=re.compile(string))

    def get_all_tags_with_str(self, tag, string):
        """ Return a list of tags of the given tag that contains the 
        given string """
        return self.soup.find_all(tag, string=string)

    def get_all_tags(self, tag):
        return self.soup.find_all(tag)

    def get_first_tag(self, tag):
        return self.soup.find(tag)
    
    def get_all_tags_with_class(self, tag, cls):
        return self.soup.find_all(tag, attrs={'class': cls})

    def get_first_tag_with_class(self, tag, cls):
        return self.soup.find(tag, attrs={'class': cls})

    def get_all_tags_with_id(self, tag, id):
        return self.soup.find_all(tag, attrs={'id': id})

    def get_first_tag_with_id(self, tag, id):
        return self.soup.find(tag, attrs={'id': id})
    
    def get_first_occurrence_str(self, string):
        """ Return the first occurrence of the given string """
        return self.soup.find(string=re.compile(string))

    def set_soup(self, soup):
        self.soup = soup

    def get_soup(self):
        return self.soup