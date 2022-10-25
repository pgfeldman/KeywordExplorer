import re
from typing import Dict, Pattern, Union

class PatternCounter:
    pattern:str
    regex:Pattern
    match_count:int

    def __init__(self, pattern:str):
        self.pattern = pattern
        self.regex = re.compile(pattern)
        self.match_count = 0

    def evaluate(self, s:str):
        self.match_count += len(self.regex.findall(s))

    def get_count(self) -> int:
        return self.match_count

    def clear_count(self):
        self.match_count = 0

class PatternCounters:
    pc_dict:Dict
    total:int

    def __init__(self):
        self.pc_dict = {}
        self.total = 0

    def add(self, pc:PatternCounter, name:str = None):
        if name != None:
            self.pc_dict[name] = pc
        else:
            self.pc_dict[pc.regex] = pc

    def find(self, name:str) -> Union[None, PatternCounter]:
        if name in self.pc_dict:
            return self.pc_dict[name]
        else:
            return None

    def evaluate(self, s:str):
        pc:PatternCounter
        for key, pc in self.pc_dict.items():
            pc.evaluate(s)

    def get_percent(self, name:str) -> float:
        self.get_total()
        if name in self.pc_dict:
            pc = self.pc_dict[name]
            return float(pc.match_count/self.total) * 100
        return 0.0

    def get_total(self) -> int:
        self.total = 0
        pc:PatternCounter
        for key, pc in self.pc_dict.items():
            self.total += pc.match_count
        return self.total


def main():
    s_list = [''']][[text: @MatteFleischer @PierreKory I thought you meant that you meant that there would be no pharmacists at your wedding. I assumed it meant that your wife and children were covered under a policy that required them to get vaccinated and that it mandated Paxlovid. That is an assumption I made. || created: 2022-09-03 22:34:18 || keyword: all_keywords || location: The Netherlands || probability: forty]][[text: RT @JessLooking8: @PierreKory Paxlovid is now COVID-19. Why did their doctors tell you this?!''',
    ''']][[text: @JFK_jeffrey @Laurie_Garrett @RepMaximax That’s all I had. I have Covid and severe COVID rebound. I'm at a late rebound stage. I was vaccinated on Paxlovid. Unfortunately my immune system didn’t respond to Paxlovid until it got to a peak that I had a fever of 109 degrees and needed a temperature of 88 degrees. I had no symptoms and it took me about 2 days to feel better. Unfortunately I had Covid. || created: 2022-09-06 03:27:11''',
    ''']][[text: @Karl_Lauterbach Kombi wo ich zu tun Paxlovid, wenn Sie das Paxlovid d… || created: 2022-09-06 12:28:40 || keyword: all_keywords || location: Baden-Württemberg || probability: thirty]][[text: RT @PierreKory: Instead of waiting for FLCCC member research papers to pass peer-review &amp; then retract w/out basis, now they send Federal p… || created: 2022-09-06 12:28:26 || keyword: all_''',
    ''']][[text: RT @mafifee_: Der perfekte Bürger vertraut 8Mäuse, ist 4xgeimpft, 2xgeboostert, nimmt Paxlovid, trägt Maske, hasst Putin, hasst Ungeimpfte,… || created: 2022-09-03 01:59:49 || keyword: all_keywords || location: Bayern, Deutschland || probability: forty]][[text: @Laurie_Garrett @thechosenone @PierreKory They should get the boosters? || created''',
    ''']][[text: @kreiner_chung @tomtomtokenshine @TomFinch @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokenshine @tomtokensh''',
    ''']][[text: RT @myrabatchelder: US is heading into disaster #COVID fall/winter. Vaccines are great but were never only thing we needed to do. And now w… || created: 2022-09-05 03:42:16 || keyword: all_keywords || location: None || probability: forty]][[text: RT @sfchronicle: OPINION:"For more than two years I basically lived like a hermit to avoid COVID.But this summer was my sister’s 40th b… || created: 2022-09-05 03:40:40 ||''',
    ''']][[text: @Karl_Lauterbach Sie der Woche || created: 2022-09-05 03:13:52 || keyword: all_keywords || location: None || probability: forty]][[text: @Karl_Lauterbach Woche Sie. || created: 2022-09-07 00:56:12 || keyword: all_keywords || location: None || probability: thirty]][[text: RT @mafifee_: Der perfekte Bürger vertraut 8Mäuse, ist 4xgeimpft, 2xgeboostert,''',
    ''']][[text: @GretaB2727 @ClaireBarrett @AlexBerenson @laurie_stevens_ @AlexBerenson @krebioffici @sfchronicle @sfchronicle We have some good news: https://t.co/HVVd3I6d3b || created: 2022-09-03 13:38:45 || keyword: all_keywords || location: None || probability: thirty]][[text: @AdamMcBeth @ClaireBarrett @AlexBerenson @laurie_stevens''',
    ''']][[text: RT @MrJonasDanner: Von "Kurve abflachen" zu "Beugehaft für Ungeimpfte".Von "15 Tagen" zu "30 Monaten".Von "wir halten zusammen" zu "verpf… || created: 2022-09-05 22:48:39 || keyword: all_keywords || location: Vosschwürzburg || probability: thirty]][[text: RT @PierreKory: Instead of waiting for FLCCC member research papers to pass peer''',
    ''']][[text: @lithohedron @mafifee_ @Karl_Lauterbach Das ich mit dem Anwendung der Suche ist einhornen ähnlich nicht bekommt es nicht? || created: 2022-09-03 21:01:43 || keyword: all_keywords || location: None || probability: thirty]][[text: @Karl_Lauterbach Wir schon Paxlovid könnte das ist: ich haben auf die Verlauf zu hilft,''']

    pcs = PatternCounters()
    pcs.add(PatternCounter(r"\w+: ten"), "ten %")
    pcs.add(PatternCounter(r"\w+: twenty"), "twenty %")
    pcs.add(PatternCounter(r"\w+: thirty"), "thirty %")
    pcs.add(PatternCounter(r"\w+: forty"), "forty %")

    for s in s_list:
        pcs.evaluate(s)

    print("Total = {}".format(pcs.get_total()))
    pc:PatternCounter
    for name, pc in pcs.pc_dict.items():
        print("{} = {} {:.1f}%".format(name, pc.match_count, pcs.get_percent(name)))
        #print("comma = {:.2f}%, period = {:.2f}%".format(pcs.get_percent("comma"), pcs.get_percent("period")))

if __name__ == "__main__":
    main()

