package cache_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/thatmattlove/hyperglass/core/infrastructure/cache"
)

func Test_Cache(t *testing.T) {
	name := "test"
	c, err := cache.New(name)
	assert.NoError(t, err)

	t.Run("get/set values", func(t *testing.T) {
		key := "test-key"
		value := "test-value"
		err := c.Set(key, value)
		assert.NoError(t, err)
		valueC, err := c.Get(key)
		assert.NoError(t, err)
		assert.Equal(t, value, valueC)
	})
	t.Cleanup(func() {
		err := c.Destroy(name)
		assert.NoError(t, err)
	})
}
