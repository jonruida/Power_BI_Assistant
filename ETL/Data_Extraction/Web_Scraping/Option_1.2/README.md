pwsh(Power_BI_Scraper)-> # mitmdump -w outfile "~h X-PowerBI" 

python Selenium_mitmproxy_PBI_O1.ipynb

python read_dumpfile_to_file.py "outfile" "readfile"    

python gzip_readfile.py
