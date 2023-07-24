package controllers

import (
	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
	"github.com/thatmattlove/hyperglass/core/entities"
	"github.com/thatmattlove/hyperglass/core/interfaces"
)

func QueryController(ctx *fiber.Ctx) error {
	var query *entities.QueryRequest
	err := ctx.BodyParser(&query)
	if err != nil {
		return err
	}
	validate := validator.New()
	err = validate.Struct(query)
	if err != nil {
		return err
	}
	iface, err := interfaces.NewQueryInterface(ctx, query)
	if err != nil {
		return err
	}
	res, err := iface.Query()
	if err != nil {
		return err
	}
	return ctx.Status(200).JSON(res)
}
