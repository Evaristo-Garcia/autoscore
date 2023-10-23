        // Sample JSON data
        var jsonData = [
            {
                "name": "John Doe",
                "age": 25,
                "email": "johndoe@example.com"
            },
            {
                "name": "Jane Smith",
                "age": 30,
                "email": "janesmith@example.com"
            },
            {
                "name": "Bob Johnson",
                "age": 40,
                "email": "bjohnson@example.com"
            }
        ];

        // Function to generate the table rows from JSON data
        function generateTableRows(data) {
            var tableBody = document.getElementById("myTable").getElementsByTagName('tbody')[0];
            var newRow, nameCell, ageCell, emailCell;

            for (var i = 0; i < data.length; i++) {
                newRow = tableBody.insertRow(tableBody.rows.length);
                nameCell = newRow.insertCell(0);
                ageCell = newRow.insertCell(1);
                emailCell = newRow.insertCell(2);

                nameCell.innerHTML = data[i].name;
                ageCell.innerHTML = data[i].age;
                emailCell.innerHTML = data[i].email;
            }
        }

        // Call the function to generate the table
        generateTableRows(jsonData);