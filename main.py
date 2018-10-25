import sys
import json
import progressbar
import codecs
import string

def get_documents_urls(parsed_json):
    """This function takes a JSON file with Instapaper highlights extracted using 
    'Instapaper highlights exporter' chrome extension and 
    
    Arguments:
        parsed_json {json} -- JSON file with Instapaper highlights

    Returns:
        [list] -- List with all unique urls for the highlighted documents
    """
    urls = set()
    for highlight in parsed_json:
        urls.add(highlight['source'])
    return urls

def clean_title(title_set):
    return repr(title_set).replace('{','').replace('}','').replace('\'','').replace('"','').rstrip('.').strip()

def process_url(url, parsed_json):
    """Process one URL for a specific highlighted document
    
    Arguments:
        url {URL} -- unique URL of the document in the JSON file
        parsed_json {json} -- JSON file with Instapaper highlights
    
    Returns:
        [dictionary] -- Dictionary with 'url', 'title' and list of highlights
    """
    document = {}
    document['url'] = url
    document['title'] = clean_title(set([x['title'] for x in parsed_json if x['source'] == url]))
    document['highlights'] = [x['highlight'] for x in parsed_json if x['source'] == url]
    return document

def get_filename_from_title(title):
    printable = set(string.ascii_letters)
    printable.add(' ')
    return ''.join(filter(lambda x : x in printable, title)).strip().replace(' ', '_') + '.md'
    
def process_document(document):
    output_path = get_filename_from_title(document['title'])
    with codecs.open(output_path, 'w', 'utf-8') as f:
        f.write('# ' + document['title'] + '\n')
        f.write('[Source](' + document['url'] + ')' + '\n')
        # we need to reverse the highlights as they are in the wrong order
        for line in document['highlights'][::-1]:
            f.write(line + '\n')

def process_json(json_file):
    # open the JSON file and parse it
    with open(json_file, encoding='utf8') as json_data:
        parsed_json = json.load(json_data)

        # highlights in JSON are stored one after the other even when they belong
        # to different documents; in order to identify the different documents 
        # I will use the `url` as the key as two different documents could have the
        # same title
        urls = get_documents_urls(parsed_json)

        # process highlights for each document
        status = 0
        bar = progressbar.ProgressBar(max_value=len(urls))
        documents= []
        for url in urls:
            # progress bar
            bar.update(status)        
            status = status + 1

            # process documents
            document = process_url(url, parsed_json)
            documents.append(document)
        bar.finish()

        # generate one markdown file per document
        status = 0
        bar = progressbar.ProgressBar(max_value=len(documents))
        for document in documents:
            # progress bar
            bar.update(status)        
            status = status + 1

            # process document
            process_document(document)

def main():
    if (len(sys.argv) == 2):
        process_json(sys.argv[1])
    else:
        print('Usage: \npython main.py file_highlights.json')
  
if __name__== "__main__":
    main()