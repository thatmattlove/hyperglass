package models

import (
	"github.com/google/uuid"
)

type Proxy struct {
	Model
	Name         string
	Address      string
	CredentialID uuid.UUID
	Credential   Credential
	Devices      []Device
}

func (Proxy) TableName() string {
	return "proxies"
}
