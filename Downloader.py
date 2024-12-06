import requests
from typing import Optional

#Class for handling a single download. The function main functionality is to take an url and download it into the path
class Downloader(object):

    #uses a url link and a destination to download a file. Optionally one can use an alt url if applicaple
    #Returns success is file got downlaoded
    def download(self,url : str, destination_path : str, alt_url : Optional[str] = None, timeout: float = 30.0) -> bool:

        success = True
        if not url and not alt_url:
            return False
        #Tries downloading with the main url
        try:
            response = requests.get(url,stream = True, timeout=timeout)

            #Checks if the status code is 200
            if response.status_code != 200:
                raise Exception(f"Bad status code: {response.status_code}")

            #Checks if the response might be a pdf file
            #Content-Type is not required nor very strict
            content_type = response.headers.get("content-type")
            if content_type:
                content_pdf = "application/pdf" in content_type
                content_data = "application/octet-stream" in content_type
                if not content_pdf and not content_data:
                    raise Exception("Not pdf type")
        except:
            success = False
        
        #If it fails to download try the alternative url
        if not success:
            try:
                response = requests.get(alt_url, stream = True, timeout=timeout)
                #Checks if the response was a pdf file
                if not "application/pdf" in response.headers.get("content-type"):
                    raise Exception("Not pdf type")

                success = True
            except:
                return False
       
        #Sace file to the distination
        with open(destination_path, "wb") as file:
            try:
                content = response.content

                #Checks if content head is PDF magic number
                if content[:4] != '%PDF'.encode():
                    raise Exception("Not pdf type")

                file.write(content)
            except:
                return False
        return success
if __name__ == "__main__":  # pragma: no cover
    downloader = Downloader()
    downloader.download("http://arpeissig.at/wp-content/uploads/2016/02/D7_NHB_ARP_Final_2.pdf", "test.pdf")
