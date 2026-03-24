document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const menuBtn = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuBtn && sidebar) {
        menuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && 
                !sidebar.contains(e.target) && 
                !menuBtn.contains(e.target) && 
                sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }

    // Auto-dismiss flash messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    // Apply persisted dark mode and language on every page load
    if (localStorage.getItem('darkmode') === '1') {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
    const translations = {
        hi: {
            'Dashboard': 'डैशबोर्ड', 'Grades': 'अंक', 'Attendance': 'उपस्थिति', 'Events': 'इवेंट्स', 'Notices': 'सूचनाएँ', 'Profile': 'प्रोफ़ाइल', 'Settings': 'सेटिंग्स', 'Help': 'सहायता', 'Logout': 'लॉगआउट', 'Users': 'यूज़र', 'Students': 'छात्र', 'Courses': 'कोर्स', 'Enrollments': 'नामांकन', 'Notifications': 'सूचनाएँ', 'Search': 'खोज', 'Welcome': 'स्वागत', 'Dark Mode': 'डार्क मोड', 'English': 'अंग्रेज़ी', 'Hindi': 'हिन्दी', 'Spanish': 'स्पेनिश', 'Faculty Dashboard': 'फैकल्टी डैशबोर्ड', "Here's your teaching overview.": 'यहाँ आपकी शिक्षण जानकारी है।', 'Assigned Courses': 'आवंटित कोर्स', 'Total Students': 'कुल छात्र', 'Open': 'खोलें', 'Mark Attendance': 'उपस्थिति दर्ज करें', 'Manage Grades': 'अंक प्रबंधन', 'Admin Dashboard': 'प्रशासन डैशबोर्ड', 'Overview of system activity and management.': 'सिस्टम गतिविधि और प्रबंधन का अवलोकन।', 'Total Users': 'कुल यूज़र', 'Total Notices': 'कुल सूचनाएँ', 'Total Events': 'कुल इवेंट्स', 'Quick Actions': 'त्वरित क्रियाएँ', 'Create Notice': 'सूचना बनाएँ', 'Create Event': 'इवेंट बनाएँ', 'Recent Notices': 'हाल की सूचनाएँ', 'View All': 'सभी देखें', 'Title': 'शीर्षक', 'Category': 'श्रेणी', 'Date': 'तारीख', 'Actions': 'क्रियाएँ', 'No recent notices.': 'कोई हाल की सूचना नहीं।', 'Upcoming Events': 'आगामी इवेंट्स', 'Location': 'स्थान', 'No upcoming events.': 'कोई आगामी इवेंट नहीं।', 'Stay updated with the latest college happenings and upcoming events.': 'नवीनतम कॉलेज गतिविधियों और आगामी इवेंट्स से अपडेट रहें।', 'Latest Notices': 'नवीनतम सूचनाएँ', 'No new notices.': 'कोई नई सूचना नहीं।', 'Upcoming Events': 'आगामी इवेंट्स', 'No upcoming events.': 'कोई आगामी इवेंट नहीं।', '© 2024 College Notification System. All rights reserved.': '© 2024 कॉलेज सूचना प्रणाली. सर्वाधिकार सुरक्षित।', 'Success is the sum of small efforts, repeated day in and day out.': 'सफलता छोटे प्रयासों का योग है, जो हर दिन दोहराए जाते हैं।'
        },
        es: {
            'Dashboard': 'Tablero', 'Grades': 'Calificaciones', 'Attendance': 'Asistencia', 'Events': 'Eventos', 'Notices': 'Avisos', 'Profile': 'Perfil', 'Settings': 'Configuración', 'Help': 'Ayuda', 'Logout': 'Cerrar sesión', 'Users': 'Usuarios', 'Students': 'Estudiantes', 'Courses': 'Cursos', 'Enrollments': 'Inscripciones', 'Notifications': 'Notificaciones', 'Search': 'Buscar', 'Welcome': 'Bienvenido', 'Dark Mode': 'Modo Oscuro', 'English': 'Inglés', 'Hindi': 'Hindi', 'Spanish': 'Español', 'Faculty Dashboard': 'Panel de Profesores', "Here's your teaching overview.": 'Aquí está su resumen de enseñanza.', 'Assigned Courses': 'Cursos Asignados', 'Total Students': 'Total de Estudiantes', 'Open': 'Abrir', 'Mark Attendance': 'Marcar Asistencia', 'Manage Grades': 'Gestionar Calificaciones', 'Admin Dashboard': 'Panel de Administración', 'Overview of system activity and management.': 'Resumen de la actividad y gestión del sistema.', 'Total Users': 'Total de Usuarios', 'Total Notices': 'Total de Avisos', 'Total Events': 'Total de Eventos', 'Quick Actions': 'Acciones Rápidas', 'Create Notice': 'Crear Aviso', 'Create Event': 'Crear Evento', 'Recent Notices': 'Avisos Recientes', 'View All': 'Ver Todo', 'Title': 'Título', 'Category': 'Categoría', 'Date': 'Fecha', 'Actions': 'Acciones', 'No recent notices.': 'No hay avisos recientes.', 'Upcoming Events': 'Próximos Eventos', 'Location': 'Ubicación', 'No upcoming events.': 'No hay eventos próximos.', 'Stay updated with the latest college happenings and upcoming events.': 'Manténgase actualizado con los últimos acontecimientos y próximos eventos universitarios.', 'Latest Notices': 'Últimos Avisos', 'No new notices.': 'No hay avisos nuevos.', 'Upcoming Events': 'Próximos Eventos', 'No upcoming events.': 'No hay eventos próximos.', '© 2024 College Notification System. All rights reserved.': '© 2024 Sistema de Notificación Universitaria. Todos los derechos reservados.', 'Success is the sum of small efforts, repeated day in and day out.': 'El éxito es la suma de pequeños esfuerzos, repetidos día tras día.'
        }
    };
    function translateUI(lang) {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (lang === 'en') el.textContent = key;
            else if (translations[lang] && translations[lang][key]) el.textContent = translations[lang][key];
        });
    }
    const lang = localStorage.getItem('lang') || 'en';
    translateUI(lang);
});
