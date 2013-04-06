import mimetypes
import os, urllib2, httplib

def post_multipart(url, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)

    headers = { 'content-type' : content_type, 
            'content-length': str(len(body))}
    req = urllib2.Request(url, body, headers)
    response = urllib2.urlopen(req).read()
    return response
    

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return (content_type, body)

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def test():
    fname = '/home/ning/Desktop/Screenshot.png'
    f1 = ('uploadedfile', os.path.basename(fname), open(fname).read())
    rst = post_multipart('localhost:9999', '/uploader.php', [], [f1])
    print rst
