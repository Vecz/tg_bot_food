from gino import Gino
db = Gino()

class Food(db.Model):
    __tablename__ = "food"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable = False, unique = True)
    first1 = db.Column(db.String, nullable = False)
    first2 = db.Column(db.String, nullable = False)
    second1 = db.Column(db.String, nullable = False)
    second2 = db.Column(db.String, nullable = False)
    third1 = db.Column(db.String, nullable = False)
    third2 = db.Column(db.String, nullable = False)
    snack1 = db.Column(db.String, nullable = False)
    snack2 = db.Column(db.String, nullable = False)

class DBfunc:  
    async def get(self, user_id):
        food = await Food.query.where(Food.user_id == user_id).gino.first()
        return food
    
    async def add(self, user_id, first1,first2,second1,second2,third1,third2,snack1,snack2):
        await Food.create(user_id = user_id, first1 = first1, first2 = first2, second1 = second1, second2 = second2, third1 = third1,\
            third2 = third2, snack1 = snack1, snack2 = snack2)
    
    async def update(self, what_update:str, where_update, new_value):
        user = await self.get(where_update)
        if (what_update == "first1"):
            await user.update(first1 = new_value).apply()
        elif (what_update == "first2"):
            await user.update(first2 = new_value).apply()
        elif (what_update == "second1"):
            await user.update(second1 = new_value).apply()
        elif (what_update == "second2"):
            await user.update(second2 = new_value).apply()
        elif (what_update == "third1"):
            await user.update(third1 = new_value).apply()
        elif (what_update == "third2"):
            await user.update(third2 = new_value).apply()
        elif (what_update == "snack1"):
            await user.update(snack1 = new_value).apply()
        elif (what_update == "snack2"):
            await user.update(snack2 = new_value).apply()

    async def delete(self, user_id):
        user = await self.get(user_id)
        await user.delete()