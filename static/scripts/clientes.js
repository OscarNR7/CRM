document.addEventListener('DOMContentLoaded', function() {
    const cuadroInfo = document.getElementById('detalle-cliente');
    const botonesMostrar = document.querySelectorAll('.btn-mostrar');
    let clienteActualId = null;  // Almacena el ID del cliente actualmente mostrado

    function toggleCuadroInfo(clienteId) {
        if (cuadroInfo.style.display === 'block' && clienteId === clienteActualId) {
            // Oculta el cuadro si se está mostrando el mismo cliente
            cuadroInfo.style.display = 'none';
            clienteActualId = null;
        } else {
            // Actualiza el ID actual y muestra el cuadro
            clienteActualId = clienteId;
            cuadroInfo.style.display = 'block';
        }
    }

    function cargarInformacionCliente(clienteId) {
        if (clienteId !== clienteActualId || cuadroInfo.style.display === 'none') {
            // Cargar la información del cliente si es un cliente diferente
            fetch(`/clientes/${clienteId}/informacion/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.text();
            })
            .then(html => {
                cuadroInfo.innerHTML = html;
                toggleCuadroInfo(clienteId);  // Alterna la visibilidad según el cliente actual
            })
            .catch(error => {
                console.error('Error al cargar la información:', error);
                alert('No se pudo cargar la información del cliente. Por favor, intente nuevamente.');
            });
        } else {
            // Si es el mismo cliente, solo alterna la visibilidad
            toggleCuadroInfo(clienteId);
        }
    }

    function initialize() {
        botonesMostrar.forEach(boton => {
            boton.addEventListener('click', function(e) {
                e.preventDefault();
                const clienteId = this.getAttribute('data-id');
                if (clienteId) {
                    cargarInformacionCliente(clienteId);
                }
            });
        });

        // Evento para cerrar con ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && cuadroInfo.style.display === 'block') {
                cuadroInfo.style.display = 'none';
                clienteActualId = null; // Reiniciar el ID actual
            }
        });

        // Agregar botón de cerrar al cuadro de información si no existe
        if (!document.getElementById('btn-cerrar-cuadro')) {
            const btnCerrar = document.createElement('button');
            btnCerrar.id = 'btn-cerrar-cuadro';
            btnCerrar.className = 'btn-close';
            btnCerrar.style.position = 'absolute';
            btnCerrar.style.right = '10px';
            btnCerrar.style.top = '10px';
            cuadroInfo.style.position = 'relative';
            cuadroInfo.appendChild(btnCerrar);
            btnCerrar.addEventListener('click', () => {
                cuadroInfo.style.display = 'none';
                clienteActualId = null; // Reiniciar el ID actual
            });
        }
    }

    initialize();
});
