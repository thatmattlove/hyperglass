package terminal

import (
	"log"
	"time"

	"github.com/melbahja/goph"
	"golang.org/x/crypto/ssh"
)

type Connection struct {
	Auth    *Auth
	Address string
	Port    uint
	Client  *goph.Client
}

type ConnectionOptions struct {
	Method      AuthMethod
	Address     string
	Port        uint
	Username    string
	Password    string
	Key         string
	KeyPassword string
	Timeout     time.Duration
}

func (conn *Connection) Run(cmd string) (res string, err error) {
	defer conn.Client.Close()
	b, err := conn.Client.Run(cmd)
	if err != nil {
		return
	}
	res = string(b)
	return
}

func NewConnection(opts *ConnectionOptions) (*Connection, error) {
	sshAuth, err := NewSSHAuth(&AuthOptions{
		Method:      opts.Method,
		Username:    opts.Username,
		Password:    opts.Password,
		Key:         opts.Key,
		KeyPassword: opts.KeyPassword,
	})
	if err != nil {
		return nil, err
	}

	auth, err := sshAuth.Backend()
	if err != nil {
		return nil, err
	}
	cfg := &goph.Config{
		Auth:    *auth,
		Addr:    opts.Address,
		Port:    opts.Port,
		User:    opts.Username,
		Timeout: opts.Timeout,
		BannerCallback: func(msg string) error {
			log.Println(msg)
			return nil
		},
		Callback: ssh.InsecureIgnoreHostKey(),
	}

	client, err := goph.NewConn(cfg)
	if err != nil {
		return nil, err
	}

	connection := &Connection{
		Auth:    &sshAuth,
		Address: opts.Address,
		Port:    opts.Port,
		Client:  client,
	}
	return connection, nil
}
