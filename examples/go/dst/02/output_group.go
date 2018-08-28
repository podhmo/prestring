package models

type Group struct {
	// ID : this is unique ID for persistent
	ID bson.ObjectId  `json:"id" bson:"_id"`
	Name string  `json:"name"`
}