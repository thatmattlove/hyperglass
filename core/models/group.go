package models

type Group struct {
	Model
	Name    string
	Devices []Device
}
