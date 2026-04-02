document.addEventListener('DOMContentLoaded', () => {
    const cepInput = document.getElementById('cep-input')
    const searchBtn = document.getElementById('search-btn')
    const btnText = searchBtn.querySelector('span')
    const loader = document.getElementById('loader')
    const resultContainer = document.getElementById('result-container')
    const errorMsg = document.getElementById('error-message')

    // Elementos dos resultados
    const resCep = document.getElementById('res-cep')
    const resStreet = document.getElementById('res-street')
    const resNeighborhood = document.getElementById('res-neighborhood')
    const resCity = document.getElementById('res-city')
    const resState = document.getElementById('res-state')
    const resComplement = document.getElementById('res-complement')
    const resIbge = document.getElementById('res-ibge')
    const sourceBadge = document.getElementById('source-badge')

    // Máscara para o CEP
    cepInput.addEventListener('input', (elemento) => {
        let valor = elemento.target.value.replace(/\D/g, '')
        if (valor.length > 5) {
            valor = valor.slice(0, 5) + '-' + valor.slice(5, 8)
        }
        elemento.target.value = valor
    })

    const searchCep = async () => {
        const cep = cepInput.value.replace(/\D/g, '')

        if (cep.length !== 8) {
            showError('Por favor informe um CEP válido')
            return
        }

        setLoading(true)
        hideError()
        resultContainer.classList.add('hidden')

        try {
            const response = await fetch(`/api/consulta/${cep}`)
            const result = await response.json()
            console.log(result)

            if (response.ok) {
                displayResult(result)
            } else {
                showError(result.error || 'Erro ao buscar CEP')
            }
        } catch (error) {
            showError('Erro de conexão')
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    const displayResult = (result) => {
        const data = result
        const source = "api" // ou remove isso se não usar

        resCep.textContent = data.cep.replace(/(\d{5})(\d{3})/, '$1-$2' )
        resStreet.textContent = data.rua || 'Não informado'
        resNeighborhood.textContent = data.bairro || 'Não informado'
        resCity.textContent = data.cidade || 'Não informado'
        resState.textContent = data.estado || 'Não informado'
        resComplement.textContent = data.complemento || 'Não informado'
        resIbge.textContent = data.ibge || 'N/A'

        sourceBadge.textContent = source === 'local_db' ? 'BANCO LOCAL' : 'API EXTERNA'
        sourceBadge.className = 'badge ' + (source === 'local_db' ? 'badge-local' : 'badge-api')

        resultContainer.classList.remove('hidden')
    }

    const setLoading = (isLoading) => {
        if (isLoading) {
            loader.style.display = 'block'
            searchBtn.disabled = true
        } else {
            loader.style.display = 'none'
            searchBtn.disabled = false
        }
    }

    const showError = (message) => {
        errorMsg.textContent = message
        errorMsg.classList.remove('hidden')
    }

    const hideError = () => {
        errorMsg.classList.add('hidden')
    }

    searchBtn.addEventListener('click', searchCep)

    cepInput.addEventListener('keypress', (ev) => {
        if (ev.key === 'Enter') {
            searchCep()
        }
    })

})