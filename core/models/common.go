package models

import "gorm.io/gorm"

type Model struct {
	// ID        uuid.UUID `gorm:"primaryKey; unique; type:uuid; column:id; default:uuid_generate_v4()"`
	// CreatedAt time.Time
	// UpdatedAt time.Time
	// DeletedAt *time.Time `sql:"index"`
	gorm.Model
}
