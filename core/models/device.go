package models

import (
	"github.com/google/uuid"
)

type Device struct {
	Model
	Name         string
	Description  string
	Address      string
	Port         uint
	Platform     string
	GroupID      uuid.UUID
	Group        Group
	CredentialID uuid.UUID
	Credential   Credential
	ProxyID      *uuid.UUID
	Proxy        *Proxy
}
