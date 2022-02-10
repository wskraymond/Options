from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.cqlengine.columns import Text, UUID, Integer, UserDefinedType, Float
from cassandra.cqltypes import UserType
from cassandra.policies import WhiteListRoundRobinPolicy, DowngradingConsistencyRetryPolicy, \
    ConstantSpeculativeExecutionPolicy
from cassandra.query import tuple_factory

import uuid
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine import connection
from datetime import datetime
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model

# In this case we can construct the base ExecutionProfile passing all attributes:
profile = ExecutionProfile(
    load_balancing_policy=WhiteListRoundRobinPolicy(['127.0.0.1']),
    # Configure the speculative execution policy
    # Execute. A new query will be sent to the server every 0.5 second
    # until we receive a response, for a max number attempts of 10.
    speculative_execution_policy=ConstantSpeculativeExecutionPolicy(delay=.5, max_attempts=10),
    retry_policy=DowngradingConsistencyRetryPolicy(),
    consistency_level=ConsistencyLevel.LOCAL_QUORUM,
    serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
    request_timeout=15,
    row_factory=tuple_factory
)
'''
#Users are free to setup additional profiles to be used by name:
profile_long = ExecutionProfile(request_timeout=30)
cluster = Cluster(execution_profiles={'long': profile_long})
session = cluster.connect()
session.execute(statement, execution_profile='long')
'''

'''
The set of IP addresses we pass to the Cluster is simply an initial set of contact points. After the driver connects to one of these nodes it will automatically discover the rest of the nodes in the cluster and connect to them, so you don’t need to list every node in your cluster.
'''
cluster = Cluster(['192.168.0.1', '192.168.0.2'], execution_profiles={EXEC_PROFILE_DEFAULT: profile})

# To establish connections and begin executing queries
session = cluster.connect()

# You can always change a Session’s keyspace using set_keyspace() or by executing a USE query:
session.set_keyspace('users')
# session.execute('USE users')

'''
1. This will transparently pick a Cassandra node to execute the query against and handle any retries that are necessary if the operation fails.
2. By default, each row in the result set will be a namedtuple. Each row will have a matching attribute for each column defined in the schema, such as name, age, and so on. You can also treat them as normal tuples by unpacking them or accessing fields by position. 
'''
rows = session.execute('SELECT name, age, email FROM users')
for row in rows:
    print(row.name, row.age, row.email)

user_lookup_stmt = session.prepare("SELECT * FROM users WHERE user_id=?")

# Default : uses the profile one
# set a default consistency level for every execution of the prepared statement:
user_lookup_stmt.consistency_level = ConsistencyLevel.QUORUM

user_ids_to_query = []
users = []
for user_id in user_ids_to_query:
    user = session.execute(user_lookup_stmt, [user_id])
    users.append(user)

'''
The driver supports asynchronous query execution through execute_async(). Instead of waiting for the query to complete and returning rows directly, this method almost immediately returns a ResponseFuture object. There are two ways of getting the final result from this object.
'''


def handle_success(rows):
    user = rows[0]
    try:
        print(user.name, user.age, user.id)
    except Exception:
        print("Failed to process user %s", user.id)
        # don't re-raise errors in the callback


def handle_error(exception):
    print("Failed to fetch user info: %s", exception)


user_id = 1234
future = session.execute_async(user_lookup_stmt, [user_id])
future.add_callbacks(handle_success, handle_error)

# Compare and Set
session.execute("INSERT INTO t (k,v) VALUES (0,0) IF NOT EXISTS")
session.execute("UPDATE t SET v = 1, x = 2 WHERE k = 0 IF v =0 AND x = 1")

'''
_____________________________________ORM___________________________________________________
'''


# first, define a model
class ExampleModel(Model):
    example_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    example_type = columns.Integer(index=True)
    created_at = columns.DateTime()
    description = columns.Text(required=False)


# the list of hosts will be passed to create a Cluster() instance
connection.setup(hosts=['127.0.0.1'], default_keyspace="cqlengine", protocol_version=3)

# create your CQL table
sync_table(ExampleModel)

# insert rows
em1 = ExampleModel.create(example_type=0, description="example1", created_at=datetime.now())
em2 = ExampleModel.create(example_type=1, description="example2", created_at=datetime.now())

print(ExampleModel.objects.count())

q = ExampleModel.objects(example_type=1)
print(q.count())

for instance in q:
    print(instance.description)

# query objects are immutable, so calling filter returns a new query object
q2 = q.filter(example_id=em1.example_id)

for instance in q2:
    print(instance.description)


'''
   UDT(User Defined Type)
   CQL:  CREATE TYPE address (street text, zip int);
'''
session.execute("CREATE TYPE address (street text, zipcode int)")
session.execute("CREATE TABLE users (id int PRIMARY KEY, location frozen<address>)")

'''
  Map a Class to a UDT
'''
# create a class to map to the "address" UDT
class Address(object):

    def __init__(self, street, zipcode):
        self.street = street
        self.zipcode = zipcode

cluster.register_user_type('mykeyspace', 'address', Address)

# insert a row using an instance of Address
session.execute("INSERT INTO users (id, location) VALUES (%s, %s)",
                (0, Address("123 Main St.", 78723)))

# results will include Address instances
results = session.execute("SELECT * FROM users")
row = results[0]
print(row.id, row.location.street, row.location.zipcode)


'''
   User Defined Types column
        cqlengine models User Defined Types (UDTs) much like tables, with fields defined by column type attributes. However, UDT instances are only created, presisted, and queried via table Models. A short example to introduce the pattern:
'''
class MyAddress(UserType):
    street = Text()
    zipcode = Integer()

class Users(Model):
    __keyspace__ = 'account'
    name = Text(primary_key=True)
    addr = UserDefinedType(MyAddress)

users.create(name="Joe", addr=MyAddress(street="Easy St.", zipcode=99999))
user = users.objects(name="Joe")[0]
print(user.name, user.addr)

'''
    Inheritance
'''
class Pet(Model):
    __table_name__ = 'pet'
    owner_id = UUID(primary_key=True)
    pet_id = UUID(primary_key=True)
    pet_type = Text(discriminator_column=True)
    name = Text()

    def eat(self, food):
        pass

    def sleep(self, time):
        pass

class Cat(Pet):
    __discriminator_value__ = 'cat'
    cuteness = Float()

    def tear_up_couch(self):
        pass

'''
   Extending Model Validation
'''

class Member(Model):
    person_id = UUID(primary_key=True)
    name = Text(required=True)

    def validate(self):
        super(Member, self).validate()
        if self.name == 'jon':
            raise ValidationError('no jon\'s allowed')

