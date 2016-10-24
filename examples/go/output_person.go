package models

// Person : this is person model
type Person struct {
	Age int  `json:"age" bson:"age"`
	Group *Group  `json:"-"`
	GroupID *bson.ObjectId  `json:"groupId,omitempty" bson:"groupId"`
	// ID : this is unique ID for persistent
	ID bson.ObjectId  `json:"id" bson:"_id"`
	Name string  `json:"name" bson:"name"`
	Status PersonStatus  `json:"status" bson:"status"`
}

type PersonStatus string

const (
	// PersonstatusHungry : maybe he or she is requesting something to eat
	PersonstatusHungry PersonStatus = "hungry"
	// PersonstatusAngry : maybe he or she is angry
	PersonstatusAngry PersonStatus = "angry"
)