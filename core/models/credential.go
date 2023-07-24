package models

import (
	"database/sql"
)

type Credential struct {
	Model
	Username string
	Mode     uint `gorm:"default:1"`
	Password sql.NullString
	Key      sql.NullString
	Devices  []Device
	Proxies  []Proxy
}
