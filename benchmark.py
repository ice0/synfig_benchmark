import requests
import os.path
import datetime
import subprocess
import json

cur_dir   = os.path.dirname(os.path.realpath(__file__)) # without trailing slash
data_dir  = cur_dir + "/data/" # trailing slash is mandatory
tests_dir = cur_dir + "/tests/"
url = "https://api.github.com/repos/synfig/synfig/releases"
apps = []

tests = []

def get_appimage(release):
    assets = release['assets']
    for asset in assets:
        url = asset['browser_download_url']
        if (url.find('.appimage') >= 0 and url.find('linux64') >= 0):
            print(asset['name'])
            print(url)
            #print(asset)
            file_name = data_dir + asset['name']
            apps.append({"tag": release['tag_name'], "file": file_name})
            if (not os.path.isfile(file_name)):
                print(file_name + " not found. Downloading...")
                os.system('aria2c --dir={dir} -s8 -x8 -c -k5M "{url}"'.format(dir=data_dir,url=url))
                os.system('chmod +x {file}'.format(file=file_name))


def download_releases():
    r = requests.get(url)
    releases = r.json()

    for r in releases:
        print("\n" + r['name'])
        print(r['tag_name'])
        get_appimage(r)


def run_test(app, test, resolution):

    res = resolution.split('x')
    res = ['-w', res[0], '-h', res[1]]

    params = [test, '--start-time', '0', '--end-time', '1'] + res

    start_time = datetime.datetime.now()
    cmd = [app["file"], '--appimage-exec', 'synfig'] + params
    print("command line: ")
    print(cmd)
    rc = subprocess.run(cmd)
    delta = datetime.datetime.now() - start_time

    return {
        "date": start_time.strftime("%Y-%m-%d %H:%M:%S"), 
        "app": app["tag"], 
        "test": test, 
        "return_code": rc.returncode,
        "elapsed_time": str(delta.microseconds),
        "resolution": resolution,
        "cmd": ' '.join(cmd)
    }


def do_tests():
    today = datetime.datetime.now()
    filename = today.strftime("benchmark_%Y-%m-%d_%H:%M:%S.json")
    results = []
    resolutions = [
        '128x128',
        '512x512'
        #['-w', '1024', '-h', '1024'],
        #['-w', '2048', '-h', '2048'],
    ]

    tests = load_tests()

    for test in tests:
        for resolution in resolutions:
            for app in apps:

                data = run_test(app, test, resolution)
                
                with open(filename, 'w') as outfile:
                    results.append(data)
                    json.dump(results, outfile, indent=4, sort_keys=True)


def load_tests():
    file_list = []

    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if (file.find(".sif") >= 0):
                #print(file)
                file_list.append(os.path.join(root,file))
    #print(file_list)
    return file_list


def main():
    download_releases()
    do_tests()
    
    #test1()

if __name__ == '__main__':
    main()