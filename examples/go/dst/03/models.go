package models

type ArchiveFormat string

const (
	Tarball ArchiveFormat = "tarball"
	Zipball ArchiveFormat = "zipball"
	// Tarball : a member of ArchiveFormat
	// Zipball : a member of ArchiveFormat
)
package models

type Group struct {
	// ID : this is unique ID for persistent
	ID bson.ObjectId  `json:"id" bson:"_id"`
	Name string  `json:"name"`
}
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
	PersonstatusHungry PersonStatus = "hungry"
	PersonstatusAngry PersonStatus = "angry"
	// PersonstatusHungry : maybe he or she is requesting something to eat
	// PersonstatusAngry : maybe he or she is angry
)
