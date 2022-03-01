import difflib as dl
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Union, Callable
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class TextSimilarity:
    dict_list: List[Dict]

    def __init__(self):
        # print("Hello TextSimilarity")
        self.dict_list = [{"pair": "1:2", "dist": 0.9}]

        self.bert_model = SentenceTransformer('bert-base-nli-mean-tokens')
        # print('loaded bert model!')

    def compare_two_texts(self, t1: str, t2: str, algo: str = "bert", scalar:float = 1.0) -> float:
        # print("comparing:\n\t...{}...\n\t...{}...".format(t1[100:160], t2[100:160]))
        if t1 == "" or t2 == "":
            return 0.0
        if algo == "difflib":
            return self.difflib_compare(t1, t2) * scalar
        if algo == "bert":
            return self.bert_compare(t1, t2) * scalar
        return 0.0

    def get_sorted_dict_list(self) -> List[Dict]:
        return self.dict_list

    # See https://en.wikipedia.org/wiki/Gestalt_Pattern_Matching
    # for details
    def difflib_compare(self, t1: str, t2: str) -> float:
        ratio = dl.SequenceMatcher(None, t1, t2).quick_ratio()
        return ratio

    # return a cosine distance measurement
    def bert_compare(self, t1: str, t2: str) -> float:
        t1_embedding = np.expand_dims(self.bert_model.encode(t1), axis=0)
        t2_embedding = np.expand_dims(self.bert_model.encode(t2), axis=0)

        distance = cosine_similarity(t1_embedding, t2_embedding)
        distance = np.squeeze(distance, axis=0)[0]
        print(distance)

        return distance


def evaluate(tl_1: List, tl_2: List, ts: TextSimilarity) -> [float, List]:
    vals = []
    for t1 in tl_1:
        for t2 in tl_2:
            if t2 != t1:
                distance = ts.compare_two_texts(t1, t2)
                vals.append(distance)
                # print("distance = {}\n".format(distance))

    avg = sum(vals) / len(vals)
    return avg, vals


def main():
    text_list_1 = [
        '''The US military rule of engagement that states "shoot first and ask questions later" means that troops on the ground are trained to kill first and investigate later.
The military is using this rule in Iraq and Afghanistan, and it is pushing for its use in the US as well.
According to reports, in 2007, US troops killed more than 1,100 civilians in Iraq. None of these incidents were investigated because the US military simply declared them "combat deaths" or "enemy kills."
In 2010, the US Department of Defense reported that there were over 5,000 attacks on US forces in Afghanistan by "insurgents". According to the same report, there was only one civilian death for every 10.''',
        '''The US military rule of engagement that states "shoot first and ask questions later" means that innocent people and bystanders will inevitably be killed, and it makes the US government an accessory to this.
The word terrorism has no definition except in the eye of the beholder. To the US, terrorism is any action against them or their interests; to Israel, any Palestinian resistance is terror; to Russia, Chechen rebels are terrorists.
Terrorism is a catch-all term that justifies any kind of violence by those who use it as a justification for their own actions. It's not a word that should ever be used lightly.
Obama's policy on drones needs to change to prevent innocent lives from being lost and''',
        '''The US military rule of engagement that states "shoot first and ask questions later" means that the US should be held accountable for the deaths of civilians in Iraq.
This war is based on lies and propaganda, and the American public need to know this. The question is whether they will get to hear it before it's too late.
• Read also: US forces 'used white phosphorus in Iraq''',
        '''The US military rule of engagement that states "shoot first and ask questions later" means that the US military has the right to decide to shoot without warning.
This is exactly what happened in Iraq. The US, UK and Australia are not signatories to the International Criminal Court (ICC), so they are not legally obliged to abide by its provisions. The ICC was established in 2002 as a court of last resort with a mandate to prosecute those who commit genocide, crimes against humanity and war crimes. It can only prosecute those who have been ratified by their home countries, the US being a notable exception.
According to Principle 15 of the UN Universal Declaration of Human Rights, "everyone has the right to a nationality".'''
    ]

    text_list_2 = [
        '''The US military rule of engagement that states "only shoot when fired upon" means that an attack on an American soldier by Palestinians is the only thing that justifies a response.
The report highlights some cases, such as near the Qalandiya checkpoint in September 2015, when the Israeli army claimed that a Palestinian had tried to stab a soldier and had been shot and killed.
However, the CCTV footage showed that the young man was just walking at a distance from the soldiers and wasn't carrying any kind of knife. He was shot and killed without any apparent reason.
According to B'Tselem, out of 120 Palestinians killed by Israeli soldiers during clashes in the West Bank last year, no less''',
        '''The US military rule of engagement that states "only shoot when fired upon" means that they'll be left in a position of having to absorb the first salvo and they'll be left in a position of having to absorb the first salvo.
Of course, we know they will also fire back and the result will be a terrible, terrible conflagration that will kill hundreds of thousands of people on both sides.
Who benefits from such an awful scenario?
I don't know just who would benefit from such a scenario but I'm sure that many Americans would see this as a good opportunity to impose their views on the rest of us, including the world.
I'll''',
        '''The US military rule of engagement that states "only shoot when fired upon" means that if any U.S. military personnel are killed or injured from mob attacks by Palestinians, it will be considered to have been a premeditated attack on U.S. military forces and the American government will likely authorize a full scale invasion of Gaza.
The US State Department has issued a travel warning, warning all U.S. citizens to avoid going anywhere near the Gaza border because of the high risk of a military confrontation/invasion by the United States.
The Israeli government has declared a state of emergency and is ordering all Israeli civilians within 30 kilometers of the Gaza border to immediately evacuate their homes and head for bomb''',
        '''The US military rule of engagement that states "only shoot when fired upon" means that soldiers on the ground will only open fire when they are under direct attack.
This has led to accusations of US soldiers standing by while thousands of people have been killed and injured in the years since the overthrow of former president Saddam Hussein.
The US military did not comment on whether any changes had been made to the rules of engagement.''',
        '''The US military rule of engagement that states "only shoot when fired upon" means that US soldiers and Marines are not authorized to fire unless they are fired on by an Iraqi. US troops were ordered not to fire on the looters during the early days of the war. I guess you can see why we lost control of the country so fast. Saddam's mercenaries and Fedayeen had orders to shoot at any American soldier who was armed and in uniform, but not to shoot at any American soldier wearing civilian clothes. It takes a while for new ammunition [bullets] to arrive in the inventory of the US Army. This is one of many reasons that soldiers had no live ammunition in their rifles when they were sent into combat'''
    ]
    ts = TextSimilarity()

    avg_1, l_1 = evaluate(text_list_1, text_list_1, ts)
    avg_1_2, l_1_2 = evaluate(text_list_1, text_list_2, ts)
    avg_2, l_2 = evaluate(text_list_2, text_list_2, ts)

    # show as box and whisker chart. More info, but not as nice!
    data = [l_1, l_2, l_1_2]
    df = pd.DataFrame(data, index=['shoot first', 'fired upon', 'both'])
    ax = df.T.boxplot(column=['shoot first', 'fired upon', 'both'], grid=False)
    ax.set_title("GPT output similarity ({} texts each)".format(len(text_list_1) + 1))
    plt.show()

    # print(ts.get_sorted_dict_list())


if __name__ == "__main__":
    main()
