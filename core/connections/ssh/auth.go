package terminal

import (
	"fmt"

	"github.com/melbahja/goph"
)

type AuthMethod int

const (
	AUTH_PASSWORD AuthMethod = 0
	AUTH_KEY      AuthMethod = 1
)

type PasswordAuth struct {
	Password string
}

type KeyAuth struct {
	Key         string
	KeyPassword string
}

type AuthOptions struct {
	Method      AuthMethod
	Username    string
	Password    string
	Key         string
	KeyPassword string
}

func (a *PasswordAuth) Backend() (*goph.Auth, error) {
	auth := goph.Password(a.Password)
	return &auth, nil
}

func (a *KeyAuth) Backend() (*goph.Auth, error) {
	auth, err := goph.Key(a.Key, a.KeyPassword)
	return &auth, err
}

type Auth interface {
	Backend() (*goph.Auth, error)
}

func NewSSHAuth(opts *AuthOptions) (Auth, error) {
	switch opts.Method {
	case AUTH_PASSWORD:
		auth := &PasswordAuth{
			Password: opts.Password,
		}
		return auth, nil
	case AUTH_KEY:
		auth := &KeyAuth{
			Key:         opts.Key,
			KeyPassword: opts.KeyPassword,
		}
		return auth, nil
	default:
		return nil, fmt.Errorf("unsupported SSH auth method '%d'", opts.Method)
	}
}
