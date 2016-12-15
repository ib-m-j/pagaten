import ftplib
import os.path
import glob


deployFrom = os.path.join('c:\\','Users','Ib','einarftp','pagaten')
toDeployTypes = ['*.html','*.js','*.asp']
toDeployFiles = [os.path.join(deployFrom, x) for x in toDeployTypes]
indexFileName = os.path.join(deployFrom, 'index.html')
print(toDeployFiles)

def makeIndex(files):
    indexStart = """
    <!DOCTYPE html>
<html>
<head>
</head>
<body style="font-size:2em;">
"""
    indexEnd = """
</body>
</html>
"""
    content = ''
    f = open(indexFileName, 'w')
    f.write(indexStart)
    for file in files:
        (root, ext) = os.path.splitext(file)
        if ext in ['.html','.htm']:
            print(os.path.basename(file))
            f.write('<a href="{}" " >{}</a><br>\n'.format(os.path.basename(file),
                                                   os.path.basename(file)))
    f.write(indexEnd)
    f.close()    

def cleanDir(conn, dir):
    check = conn.pwd()
    if check == dir:
        print(' will clean')
        info = conn.mlsd()
        for name, data in info:
            if (data['type'] == 'file' and 
               os.path.splitext(name)[1] != 'html'):
                print(name)
                print(conn.delete(name))

def deploy():
    files = []
    for x in toDeployFiles:
        files.extend(glob.glob(x))
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
