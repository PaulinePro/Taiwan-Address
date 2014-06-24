# Taiwan Address

This parser tool can tell you every address in every city and cityarea.<br />
I also put the results in JSON and SQLite format, so you can grab it directly.<br />
Hope both the codes and result datas can help you.<br /><br />
Fork this repo and play around with it, don't forget to make pull request!


### Usage: ###
<pre><code>
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
</code></pre>

### Requirements ###
* Requests
* BeautifulSoup4

### Data source ###
* 中華郵政全球資訊網(中文地址英譯) - http://www.post.gov.tw/post/internet/Postal/index.jsp?ID=207

### To-Do ###
* Everything is working fine now.

### Lincense: ###
* Just do what the f*** you want!
