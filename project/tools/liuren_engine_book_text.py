"""Convert engine HTML to readable TXT; no OCR or reconstruction of images."""
from html.parser import HTMLParser
from html import unescape
from pathlib import Path
import json,re,sys,hashlib

class Text(HTMLParser):
    blocks={'p','div','h1','h2','h3','h4','h5','h6','section','article','blockquote','ul','ol','li','table','tr','pre'}
    def __init__(self):
        super().__init__(convert_charrefs=True);self.parts=[];self.images=[];self.hidden=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('script','style'):self.hidden+=1;return
        if self.hidden:return
        if tag in self.blocks or tag=='br':self.parts.append('\n')
        if tag in ('td','th') and self.parts and not self.parts[-1].endswith('\n'):self.parts.append('\t')
        if tag=='img':
            self.images.append({'index':len(self.images)+1,'src':a.get('src',''),'alt':a.get('alt','')})
            self.parts.append(f'\n[原文图片{len(self.images)}：{a.get("alt") or "课图或插图，未转录"}]\n')
        if tag=='hr':self.parts.append('\n────────\n')
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
    def handle_endtag(self,tag):
        if tag in ('script','style'):
            self.hidden=max(0,self.hidden-1);return
        if not self.hidden and tag in self.blocks:self.parts.append('\n')
    def handle_data(self,data):
        if not self.hidden:self.parts.append(data)
    def text(self):
        s=''.join(self.parts).replace('\r\n','\n').replace('\r','\n').replace('\xa0',' ')
        s=re.sub(r'[ \t]+\n','\n',s);s=re.sub(r'\n[ \t]+','\n',s)
        return re.sub(r'\n{3,}','\n\n',s).strip()+'\n'

def convert(record):
    # The engine mixes real HTML with entity-escaped headings and navigation.
    # Decode layers before tokenizing so encoded <a>/<p> never leak into TXT.
    markup=record['zhengwen']
    for _ in range(4):
        decoded=unescape(markup)
        if decoded==markup:break
        markup=decoded
    p=Text();p.feed(markup);p.close()
    return {**record,'text':p.text(),'images':p.images}

if __name__=='__main__':
    records=json.load(sys.stdin)
    json.dump([convert(x) for x in records],sys.stdout,ensure_ascii=False)
