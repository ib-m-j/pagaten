import ftplib
import os.path
import glob


deployFrom = os.path.join('c:\\','Users','Ib','einarftp','pagaten')
toDeployFiles = os.path.join(deployFrom, '*.html')
indexFileName = os.path.join(deployFrom, 'index.html')

def makeIndex(files):
    indexStart = """
    <!DOCTYPE html>
<html>
<head>
</head>
<body>
"""
    indexEnd = """
</body>
</html>
"""
    content = ''
    f = open(indexFileName, 'w')
    f.write(indexStart)
    for file in files:
        f.write('<a href="{}">{}</a><br>\n'.format(os.path.basename(file),
                                                   os.path.basename(file)))
    f.write(indexEnd)
    f.close()    

def cleanDir(conn, dir):
    check = conn.pwd()
    if check == dir:
        print(' will clean')
        info = conn.mlsd()
        for name, data in info:
            if data['type'] == 'file':
                print(name)
                print(conn.delete(name))

def deploy():
    files = glob.glob(toDeployFiles)
    makeIndex(files)
    conn = ftplib.FTP('91.250.84.226', 'einardkftp', '5uM7FtPpI')
    conn.cwd('subdomains\pagaten.einar.dk\httpdocs')
    cleanDir(conn, '/subdomains/pagaten.einar.dk/httpdocs')
    for f in files:
        data = open(f, 'rb')
        conn.storlines('STOR {}'.format(os.path.basename(f)), data)
        print('uploaded', os.path.basename(f))
        data.close()

    conn.quit()


if __name__ == '__main__':
    deploy()
