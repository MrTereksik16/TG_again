class Modes:
    RECOMMENDATIONS = 'recommendations'
    PERSONAL = 'personal'
    CATEGORIES = 'categories'


class PostTypes:
    PREMIUM = 'premium'
    PERSONAL = 'personal'
    CATEGORY = 'category'

    def __new__(cls, value: str):
        if value == cls.PREMIUM:
            return cls.PREMIUM
        if value == cls.PERSONAL:
            return cls.PERSONAL
        if value == cls.CATEGORY:
            return cls.CATEGORY


class MarkTypes:
    LIKE = 1
    DISLIKE = 2
    NEUTRAL = 3
