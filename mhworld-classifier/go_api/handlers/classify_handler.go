// go_api/handlers/classify_handler.go
package handlers

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"go_api/model"

	"github.com/gin-gonic/gin"
)

// MLService interface para o handler. Permite injeção de dependência do serviço.
type MLService interface {
	ClassifyImage(imagePath string) (model.PredictionResponse, error)
}

// ClassifyHandler é a função de handler para a rota /classify.
// Recebe uma instância de MLService para performar a classificação.
func ClassifyHandler(mlService MLService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 1. Recebe o arquivo de imagem do formulário multipart
		file, err := c.FormFile("image")
		if err != nil {
			log.Printf("Erro: Não foi possível obter o arquivo de imagem do formulário: %v", err)
			c.JSON(http.StatusBadRequest, model.PredictionResponse{Error: fmt.Sprintf("Nenhum arquivo de imagem encontrado na requisição: %v", err)})
			return
		}

		// 2. Salva a imagem temporariamente no disco
		tempDir := "temp_images"
		if err := os.MkdirAll(tempDir, os.ModePerm); err != nil {
			log.Printf("Erro: Não foi possível criar o diretório temporário '%s': %v", tempDir, err)
			c.JSON(http.StatusInternalServerError, model.PredictionResponse{Error: fmt.Sprintf("Erro interno do servidor ao criar pasta temporária: %v", err)})
			return
		}

		tempFilePath := filepath.Join(tempDir, fmt.Sprintf("%d_%s", time.Now().UnixNano(), file.Filename))
		if err := c.SaveUploadedFile(file, tempFilePath); err != nil {
			log.Printf("Erro: Não foi possível salvar o arquivo temporário '%s': %v", tempFilePath, err)
			c.JSON(http.StatusInternalServerError, model.PredictionResponse{Error: fmt.Sprintf("Erro interno do servidor ao salvar imagem: %v", err)})
			return
		}
		defer func() { // Garante que o arquivo temporário seja removido
			if err := os.Remove(tempFilePath); err != nil {
				log.Printf("Aviso: Não foi possível remover o arquivo temporário '%s': %v", tempFilePath, err)
			}
		}()

		// 3. Chama o serviço de ML para classificação
		prediction, err := mlService.ClassifyImage(tempFilePath)
		if err != nil {
			// O erro já foi logado dentro do serviço.
			c.JSON(http.StatusInternalServerError, model.PredictionResponse{Error: fmt.Sprintf("Erro na classificação de imagem: %v", err)})
			return
		}

		// 4. Retorna o resultado da previsão como JSON
		c.JSON(http.StatusOK, prediction)
	}
}
