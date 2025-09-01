## What is Object Document Mapping?  

- It is a tecnique that maps Object oriented code to document oriented databases(MongoDB).  

- By abstracting database interactions through model classes, it simplifies the process of storing and managing data in a document-oriented database like MongoDB. This approach is particularly beneficial in applications where data structures align well with object-oriented programming paradigms.  

- Our data modeling centers on creating specific document classes — UserDocument, RepositoryDocument, PostDocument, and ArticleDocument — that mirror the structure of our MongoDB collections.  

## function from_mongo and to_mongo in documents.py  

- from_mongo: This method is responsible for converting the "_id" field from a string to a UUID object. 

- to_mongo: This method is responsible for converting the "id" field from a UUID object to a string.