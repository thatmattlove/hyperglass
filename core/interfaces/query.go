package interfaces

import (
	"time"

	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
	"github.com/thatmattlove/hyperglass/core/entities"
)

type QueryInterface struct {
	Ctx     *fiber.Ctx
	Request *entities.QueryRequest
}

func (qi *QueryInterface) Query() (res any, err error) {
	res = &entities.PlainQueryResponse{
		Random:    "random string",
		Cached:    false,
		Runtime:   30,
		Timestamp: time.Now(),
		Format:    "text/plain",
		Output:    "some output",
	}
	validate := validator.New()
	err = validate.Struct(res)
	return
}

func NewQueryInterface(ctx *fiber.Ctx, req *entities.QueryRequest) (iface *QueryInterface, err error) {
	iface = &QueryInterface{
		Ctx:     ctx,
		Request: req,
	}
	return
}
