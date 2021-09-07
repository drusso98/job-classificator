import re
import utils


def get_rev_transcripts(url, pages=8):
    url_transcripts = []
    for i in range(1, pages + 1):
        link_page = url + '/page/' + str(i)
        source = utils.get_source(link_page)
        links = [link.find('a')['href'] for link in source.find_all('div', class_='fl-post-column')]
        url_transcripts.extend(links)
    return url_transcripts


def get_raw_transcript(url):
    article_html = utils.get_source(url)
    raw_text = [answer.get_text() for answer in article_html.find("div", class_='fl-callout-text').find_all("p")]
    return raw_text


def filter_rev_speakers(data):
    pattern = r"((speaker|reporter|interviewer|question)(\s\d)?|Lady\sGaga|crowd|audience|video|announcer|moderator|translator)"
    processed_data = {}
    for item in data.items():
        transcript = []
        for elem in item[1]:
            if re.search(r":\s\(\d\d:\d\d(:\d\d)?\)", elem):
                elem = re.sub(r":\s\(\d\d:\d\d(:\d\d)?\)","",elem)
            par = tuple(elem.split("\n"))
            if len(par) == 2 and re.search(pattern, par[0], re.IGNORECASE) is None:
                transcript.append(par)
        processed_data[item[0]] = transcript
    return processed_data


def get_scientific_articles(url):
    soup = utils.get_source(url)
    articles = [article for article in soup.find("div", class_="compilation").find_all("li", class_="compilation")]
    articles.pop(0)
    text_articles = []
    for i, article in enumerate(articles, 2):
        html_id = "compilation-2-" + str(i) + "-p-1"
        if article.find("figure") is not None:
            temp = article
            temp.figure.decompose()
            text_articles.append(temp.find("p").get_text())
        else:
            text_articles.append(article.find("p", {"id": html_id}).get_text())
    return text_articles


def dataset_rev_text(data):
    docs = []
    for item in data.items():
        final_doc = ""
        for text in item[1]:
            temp_txt = text[1]
            if re.search(r"\[[A-z\s’,\-\.]+\s?\d\d(\s?:\s?\d\d\s?)+\]", temp_txt):
                temp_txt = re.sub(r"\[[A-z\s’,\-\.]+\s?\d\d(\s?:\s?\d\d\s?)+\]", "", temp_txt)
            if re.search(r"\xa0", temp_txt):
                temp_txt = re.sub(r"\xa0", "", temp_txt)
            if re.search(r"\([\w\s\.]+\)", temp_txt, re.IGNORECASE):
                temp_txt = re.sub(r"\([\w\s\.]+\)", "", temp_txt)
            final_doc = final_doc + " " + temp_txt.strip()
            idx = item[1].index(text)
            data[item[0]][idx] = (text[0], temp_txt.strip())
        docs.append(final_doc)
    return data,docs


def dataset_science_text(data):
    docs = []
    for item in data.items():
        doc = " ".join(item[1])
        docs.append(doc)
    return docs


### scraping political and sport data ###
url_politics = 'https://www.rev.com/blog/transcript-category/2020-election-transcripts'
url_sport = 'https://www.rev.com/blog/transcript-category/sports-transcripts'
political_links = get_rev_transcripts(url_politics)
sport_links = get_rev_transcripts(url_sport)

# saving all the links in a txt file
file = open('data/url_transcripts_political.txt','w')
for el in political_links:
    file.write(el + '\n')
file.close()

file = open('data/url_transcripts_sport.txt','w')
for el in sport_links:
    file.write(el + '\n')
file.close()

raw_political_data = {}
for link in political_links:
    raw_political_data[link] = get_raw_transcript(link)

raw_sport_data = {}
for link in sport_links:
    raw_sport_data[link] = get_raw_transcript(link)

utils.save_pickle(raw_political_data, 'raw_political_data.pickle')
utils.save_pickle(raw_sport_data, 'raw_sport_data.pickle')

political_data = filter_rev_speakers(raw_political_data)
sport_data = filter_rev_speakers(raw_sport_data)

utils.save_pickle(political_data, 'political_data.pickle')
utils.save_pickle(sport_data, 'sport_data.pickle')

### scraping scientific data ###
issues_link = []
for year in range(2019,2022):
    url = 'https://science.sciencemag.org/content/by/year/' + str(year)
    source = utils.get_source(url)
    pre_url = "https://science.sciencemag.org"
    post_url = "/twis.full"

    links = [str(pre_url + link['href'] + post_url) for link in source.find("ul", class_="issue-month-detail").find_all("a")]
    links = list(set(links))
    issues_link.extend(links)

scientific_data = {}
for idx,issue in enumerate(issues_link):
    scientific_data[idx] = get_scientific_articles(issue)

utils.save_pickle(scientific_data,"scientific_data.pickle")

# saving scientific data in a txt file
file = open("data/scientific_data.txt", "w")
for item in scientific_data.items():
    for el in item[1]:
        file.write(el + "\n")

# creating the final dataset

dataset = {}

political_data,documents = dataset_rev_text(political_data)
dataset['politics'] = documents
sport_data,documents = dataset_rev_text(sport_data)
dataset['sport'] = documents
dataset['scientist'] = dataset_science_text(scientific_data)
utils.save_pickle(dataset,"dataset.pickle")
# saving dataset in a txt file
file = open("data/dataset.txt", "w")
utils.save_dataset(dataset, file)
file.close()
