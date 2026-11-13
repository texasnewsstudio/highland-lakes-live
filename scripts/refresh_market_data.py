#!/usr/bin/env python3
"""Refresh original on-page USDA market report excerpts without external embeds."""
import io, re, html, pathlib, datetime, urllib.request
from pypdf import PdfReader

PAGE=pathlib.Path("cattle-hay-livestock.html")
START="<!-- USDA_AUTO_START -->"
END="<!-- USDA_AUTO_END -->"
SOURCES=[
 ("Texas cattle auction summary","https://www.ams.usda.gov/mnreports/ams_1955.pdf"),
 ("Texas direct hay report","https://www.ams.usda.gov/mnreports/ams_2707.pdf"),
]
def get_report(url):
    req=urllib.request.Request(url,headers={"User-Agent":"HighlandLakesLiveMarketUpdater/1.0","Accept":"application/pdf"})
    with urllib.request.urlopen(req,timeout=35) as response:
        raw=response.read(8_000_000)
    if not raw.startswith(b"%PDF"): raise ValueError("Not a PDF")
    reader=PdfReader(io.BytesIO(raw))
    text="\n".join((page.extract_text() or "") for page in reader.pages[:3])
    lines=[re.sub(r"\s+"," ",line).strip() for line in text.splitlines()]
    lines=[line for line in lines if len(line)>3]
    if len(lines)<12: raise ValueError("Insufficient extracted report data")
    return lines
def main():
    blocks=[]
    for title,url in SOURCES:
        try: lines=get_report(url)
        except Exception as ex:
            print("Source unavailable:",title,str(ex));return
        # Preserve the report's own wording and units rather than guessing at table columns.
        excerpt=lines[:48]
        rows="".join("<tr><td>"+html.escape(line)+"</td></tr>" for line in excerpt)
        blocks.append('<article class="card" style="min-width:0"><h3>'+html.escape(title)+'</h3><p class="source">Latest fetched official USDA publication. Values retain the source report’s units and labels; consult the report date in the data below.</p><div class="tablewrap"><table><thead><tr><th>Published USDA report data</th></tr></thead><tbody>'+rows+'</tbody></table></div><p><a href="'+html.escape(url)+'" target="_blank" rel="noopener">Verify original USDA report</a></p></article>')
    section='<section class="section card"><h2>Automatically refreshed USDA market data</h2><p>Our own on-page tables, populated from the latest available USDA reports. Report publication dates may differ from the retrieval time. The historical market analysis below is preserved for comparison.</p><p class="source">Retrieved '+datetime.datetime.now(datetime.timezone.utc).strftime("%B %d, %Y at %H:%M UTC")+'</p>'+''.join(blocks)+'</section>'
    original=PAGE.read_text(encoding="utf-8")
    new=START+section+END
    if START in original and END in original:
        original=re.sub(re.escape(START)+r".*?"+re.escape(END),lambda _:new,original,flags=re.S)
    else:
        original=original.replace('<section class="section card">',new+'\n<section class="section card">',1)
    PAGE.write_text(original,encoding="utf-8")
    print("Updated USDA on-page market tables.")
if __name__=="__main__":main()
