
from flask import Flask
from flask_restful import Resource,Api,marshal_with,fields,reqparse
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

# While using SQL alchemy use engine in one file only otherwise conflict occours.



app=Flask(__name__)
api=Api(app)



#URL used for creating Engine for database access
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:0000@localhost:5432/crud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True



#By calling this constructor we initialize Engine,base for creating models,session maker and all other object to db object.
db=SQLAlchemy(app)




class UserModel(db.Model):
    __tablename__='user_details' #for specifying exixting table name -coloum name must be same for existing tables

    acc_id=db.Column(db.Integer,primary_key=True) #set the primary key field as it is and omit the field while constructor creation to auto increment
    name = db.Column(db.String(60))
    email = db.Column(db.String(70))
    phone = db.Column(db.String(10))
    pincode = db.Column(db.String(6))
 
    def __init__(self,name,email,phone,pincode):  #while creating the constructor ID cannot  needed because its auto incremented.
        self.name = name
        self.email=email
        self.phone=phone
        self.pincode=pincode

    def __repr__(self):
        return f"Donor(id={self.acc_id},name= {self.name},email= {self.email}, phone={self.phone},pincode={self.pincode}"

#

#create tables and database if not created
db.create_all()


post_req_parser=reqparse.RequestParser()
post_req_parser.add_argument('name',type=str,help='invalid name',required=True)
post_req_parser.add_argument('email',type=str,help='invalid email',required=True)
post_req_parser.add_argument('phone',type=str,help='invalid phone',required=True)
post_req_parser.add_argument('pincode',type=str,help='invalid pincode',required=True)

update_req_parser=reqparse.RequestParser()
update_req_parser.add_argument('name',type=str,help='invalid name',required=False)
update_req_parser.add_argument('email',type=str,help='invalid email',required=False)
update_req_parser.add_argument('phone',type=str,help='invalid phone',required=False)
update_req_parser.add_argument('pincode',type=str,help='invalid pincode',required=False)



try:
    #db.session.add(UserModel(name='Prem  G',email='prem@mail.com',phone='9875765476',pincode='535465'))
    #db.session.commit()
    pass
except sqlalchemy.exc.IntegrityError:
    print('record already exixts')


resource_fields={
    'acc_id':fields.String,  #thesee field names also must be same as model fields
    'name':fields.String,
    'email':fields.String,
    'phone':fields.String,
    'pincode':fields.String

    
}


def ListConvert(result):
    result_dict={}
    for record in result:
        temp_dict={}
        temp_dict['name']=record.name
        temp_dict['email']=record.email
        temp_dict['phone']=record.phone
        temp_dict['pincode']=record.pincode
        result_dict[str(record.acc_id)]=temp_dict
    print(result_dict)
    return result_dict


#db.session.add(UserModel(name='premnath',email='prem@mail.com',phone='6789876788',pincode='234534'))
#db.session.commit()

class home(Resource):
    @marshal_with(resource_fields)
    def get(self):
        res=db.session.query(UserModel).filter_by().all()
        return res


class users(Resource):

    @marshal_with(resource_fields)
    def get(self,id):
        res=db.session.query(UserModel).filter_by(acc_id=id).all()
        #result_final=ListConvert(res)
        return res

    def post(self,id):
        try:
            args=post_req_parser.parse_args()
            print(args['name'])
            user=UserModel(name=args['name'],email=args['email'],phone=args['phone'],pincode=args['pincode'])
            db.session.add(user)
            db.session.commit()
            return 201
        except sqlalchemy.exc.IntegrityError:
            return { "error":"record already exist"}
 
    def put(sefl,id):
        try:
            db.session.commit()
            args=update_req_parser.parse_args()
            data={}                             #Empty dictionary for stiring filtered input arguments
            for key in args.keys():
                if args[key] != None:           # filtering the incomming arguments by clearing keys with NONe value.
                    data[key]=args[key]
            result=db.session.query(UserModel).filter_by(acc_id=id).first()
            if not result:
                return {"Error": "Invalid Identifier"}
            
            result=db.session.query(UserModel).filter_by(acc_id=id).update(data)   #GEt the single record and update it with keys in data dictionary not use first.
            db.session.commit()             #here no add required because the record alredy stored

            return 201
        except Exception as e:
            print(e)

    def delete(self,id):
        try:
            record=UserModel.query.filter_by(acc_id=id).first()
            db.session.delete(record)               #deleting the record
            db.session.commit()
            return 200
        except Exception as e:
            print(e)
            return {"Error":"Invalid identifier"}



api.add_resource(home,"/users","/users/")
api.add_resource(users,"/users/<int:id>")

if __name__=='__main__':
    app.run(debug=True)
