from typing import Dict, Union

class PatternCounter:
    pattern:str
    match_count:int

    def __init__(self, pattern:str):
        self.pattern = pattern
        self.match_count = 0

    def evaluate(self, s:str):
        self.match_count += s.count(self.pattern)

    def get_count(self) -> int:
        return self.match_count

    def clear_count(self):
        self.match_count = 0

class PatternCounters:
    pc_dict:Dict

    def __init__(self):
        self.pc_dict = {}

    def add(self, pc:PatternCounter, name:str = None):
        if name != None:
            self.pc_dict[name] = pc
        else:
            self.pc_dict[pc.pattern] = pc

    def find(self, name:str) -> Union[None, PatternCounter]:
        if name in self.pc_dict:
            return self.pc_dict[name]
        else:
            return None

def main():
    s = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam venenatis ligula lorem, ut ornare eros condimentum porta. Maecenas mollis eleifend metus nec hendrerit. Nam ultrices in tellus molestie vehicula. Proin vehicula metus purus, et tristique nibh gravida ac. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nunc sit amet ante pretium turpis sollicitudin scelerisque. Nullam luctus, sapien ut lacinia fermentum, risus risus venenatis dolor, quis sodales tellus ex eu mauris. Sed id mattis ligula. Praesent efficitur, eros nec dignissim egestas, elit urna malesuada quam, et tristique ante est eu odio. Pellentesque bibendum malesuada nisl ac fringilla. Morbi commodo consequat tincidunt. Suspendisse id ultricies ante. Aenean imperdiet nibh non laoreet interdum. Mauris sit amet pretium justo. Quisque erat lectus, tincidunt at neque ut, consectetur pellentesque ex.'''
    comma = PatternCounter(', ')
    for i in range(3):
        comma.evaluate(s)
        print("there are {} instances of '{}' so far".format(comma.get_count(), comma.pattern))

if __name__ == "__main__":
    main()

