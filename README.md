# 台灣地址

這個 Parser tool 是因為之前寫了些 APP 需要用到全台灣的地址，但是找了很久卻沒有相關的資料庫，於是，我在中華郵政網站的「3+2 郵遞區號查詢」找到全台灣的縣市,區以及地址。<br />
希望這個工具可以幫助到更多需要用到全台灣地址的人。

### Usage: ###
<code>
    from address import Address
    a = Address()
    
    cityareas = a.cityarea(u'臺北市')
    for cityarea in cityareas:
        print cityarea
    # 中山區, 松山區, 士林區, 大同區...
    
    addresses = a.address(u'臺北市', u'中正區')
    for address in addresses:
        print address
    # 寶慶路, 羅斯福路１段, 羅斯福路２段, 羅斯福路３段, 羅斯福路４段...
</code>

### Requirements ###
* Requests
* BeautifulSoup4

    
## Data source
* 中華郵政全球資訊網(3+2郵遞區號查詢) - http://www.post.gov.tw/post/internet/Postal/index.jsp?ID=207

## To-Do
* Everything is working fine now.
