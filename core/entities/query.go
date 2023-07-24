package entities

import "time"

type QueryRequest struct {
	Devices []uint `json:"devices" validate:"min=1"`
	Target  string `json:"target" validate:"cidr|ip"`
	Type    string `json:"type" validate:"required"`
}

type PlainQueryResponse struct {
	Random    string    `json:"random" validate:"required"`
	Cached    bool      `json:"cached" validate:"boolean"`
	Runtime   float64   `json:"runtime" validate:"required"`
	Timestamp time.Time `json:"timestamp" validate:"required"`
	Format    string    `json:"format" validate:"oneof=application/json text/plain"`
	Output    string    `json:"output" validate:"required"`
}
